from typing import Annotated

from bcrypt import checkpw
from fastapi import APIRouter, Depends, HTTPException

from app.models.manager import Manager
from app.models.session import Session
from app.schemas.auth import LoginData
from app.utils import authSession

router = APIRouter(prefix="/api/v0/auth")


@router.post("/login")
async def login(data: LoginData):
    if (manager := await Manager.get_or_none(email=data.email)) is None:
        raise HTTPException(status_code=401, detail="Wrong email or password!")
    if not checkpw(data.password.encode().replace(b"\x00", b""), manager.password.encode()):
        raise HTTPException(status_code=401, detail="Wrong email or password!")

    session = await Session.create(manager=manager)
    return {"token": f"{session.id}.{manager.id}.{session.token}"}


@router.post("/logout", status_code=204)
async def logout(session: Annotated[Session, Depends(authSession)]):
    await Session.filter(id=session.id).delete()
