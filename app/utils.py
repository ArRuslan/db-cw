from typing import Union, Annotated
from uuid import UUID

from fastapi import Request, HTTPException, Depends

from app.models.manager import Manager
from app.models.session import Session


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
