from typing import Union
from uuid import UUID

from fastapi import Request, HTTPException

from app.db import database
from app.models.manager import Manager
from app.models.session import Session


class Permissions:
    ADMIN = 1 << 0
    MANAGE_ORDERS = 1 << 1


async def authManager(request: Request, session: bool=False) -> Union[Manager, Session]:
    if not (auth := request.headers.get("authorization")):
        raise HTTPException(status_code=401, detail="No such session!")

    try:
        uid, sid, key = auth.split(".")
        uid = int(uid)
        sid = int(sid)
        key = str(UUID(key))

        result = await database.fetch_one("SELECT managers.*, session_id, token FROM sessions JOIN managers "
                                          "ON sessions.manager_id = managers.manager_id WHERE session_id=:sid AND "
                                          "managers.manager_id=:uid AND token=:key",
                                          {"sid": sid, "uid": uid, "key": key})
        if result is None:
            raise ValueError

        return Session(**result) if session else Manager(**result)
    except ValueError:
        raise HTTPException(status_code=401, detail="No such session!")


async def authSession(request: Request):
    return await authManager(request, True)
