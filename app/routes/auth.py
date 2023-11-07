from typing import Annotated

from bcrypt import checkpw
from fastapi import APIRouter, Depends, HTTPException

from app.models.manager import Manager
from app.models.session import Session
from app.schemas.auth import LoginData
from app.utils import authManager, authSession

router = APIRouter(prefix="/api/v0/auth")


@router.post("/login")
async def login(data: LoginData):
    manager = await Manager.from_query("SELECT * FROM managers WHERE email=:email", {"email": data.email},
                                       many=False)
    if not checkpw(data.password.encode().replace(b"\x00", b""), manager.password.encode()):
        raise HTTPException(status_code=401, detail="Wrong email or password!")

    session = await Session.from_query("INSERT INTO sessions (manager_id) VALUES (:manager_id) "
                                       "RETURNING session_id, manager_id, token;", {"manager_id": manager.id},
                                       many=False)
    return {"token": f"{session.id}.{manager.id}.{session.token}"}


@router.post("/logout", status_code=204)
async def logout(session: Annotated[Session, Depends(authSession)]):
    await Session.delete(session.id)
