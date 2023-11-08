from typing import Union
from uuid import UUID

from fastapi import Request, HTTPException

from app.db import database
from app.models.manager import Manager
from app.models.session import Session


class Permissions:
    ADMIN = 1 << 0
    MANAGE_ORDERS = 1 << 1


async def authManager(request: Request, session_: bool=False) -> Union[Manager, Session]:
    if not (auth := request.headers.get("authorization")):
        raise HTTPException(status_code=401, detail="No such session!")

    try:
        uid, sid, key = auth.split(".")
        uid = int(uid)
        sid = int(sid)
        key = str(UUID(key))

        if (session := await Session.get_or_none(id=sid, manager__id=uid, token=key).select_related("manager")) is None:
            raise ValueError

        return session if session_ else session.manager
    except ValueError:
        raise HTTPException(status_code=401, detail="No such session!")


async def authSession(request: Request):
    return await authManager(request, True)
