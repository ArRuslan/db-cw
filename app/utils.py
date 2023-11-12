from typing import Union, Annotated, Type
from uuid import UUID

from fastapi import Request, HTTPException, Depends
from tortoise.expressions import Q

from app.models._utils import Model
from app.models.manager import Manager
from app.models.session import Session
from app.schemas import SearchData


class Permissions:
    ADMIN = 1 << 0
    MANAGE_ORDERS = 1 << 1
    MANAGE_CATEGORIES = 1 << 2
    MANAGE_PRODUCTS = 1 << 3
    MANAGE_CUSTOMERS = 1 << 4
    EXECUTE_SQL = 1 << 5
    READ_STATISTICS = 1 << 6

    DEFAULT = MANAGE_ORDERS | MANAGE_CATEGORIES | MANAGE_PRODUCTS | MANAGE_CUSTOMERS | READ_STATISTICS

    @staticmethod
    def check(manager: Manager, perm: int) -> bool:
        return manager.permissions & Permissions.ADMIN == Permissions.ADMIN or manager.permissions & perm == perm


async def authManager(request: Request, session_: bool=False) -> Union[Manager, Session]:
    if not (auth := request.headers.get("authorization")):
        raise HTTPException(status_code=401, detail="No such session!")

    try:
        sid, uid, key = auth.split(".")
        uid = int(uid)
        sid = int(sid)
        key = UUID(key)

        if (session := await Session.get_or_none(id=sid, manager__id=uid, token=key).select_related("manager")) is None:
            print(1)
            raise ValueError

        return session if session_ else session.manager
    except ValueError:
        raise HTTPException(status_code=401, detail="No such session!")


async def authSession(request: Request):
    return await authManager(request, True)


AuthManagerDep = Annotated[Manager, Depends(authManager)]
AuthSessionDep = Annotated[Manager, Depends(authManager)]


SEARCH_SUFFIX = {
    ">": "__gt",
    ">=": "__ge",
    "<": "__lt",
    "<=": "__le",
    "contains": "__icontains",
    "startsWith": "__istartswith",
    "endsWith": "__iendswith",
    "isEmpty": "__isnull",
    "isNotEmpty": "__not_isnull",
    "isAnyOf": "__in",
    "!=": "__not",

    "=": "",
    "equals": "",
}


def search(model: Type[Model], data: SearchData):
    fields = set(model.__annotations__.keys())
    query = model.all().limit(data.pagination.pageSize).offset(data.pagination.pageSize * data.pagination.page)
    filter_query = None
    for item in data.filter.items:
        filter_key = item.field
        if filter_key not in fields or item.value is None or item.operator not in SEARCH_SUFFIX:
            continue

        filter_key += SEARCH_SUFFIX[item.operator]
        q = Q(**{filter_key: item.value})

        if filter_query is None:
            filter_query = q
            continue

        if data.filter.logicOperator == "or":
            filter_query |= q
        else:
            filter_query &= q

    if filter_query is not None:
        query = query.filter(filter_query)

    orderings = []
    for sort_item in data.sort:
        if sort_item.field not in fields:
            continue
        if sort_item.sort == "desc":
            sort_item.field = f"-{sort_item.field}"
        orderings.append(sort_item.field)

    if orderings:
        query = query.order_by(*orderings)

    return query
