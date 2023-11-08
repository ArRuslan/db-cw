from bcrypt import hashpw, gensalt
from fastapi import APIRouter

from app.db import database
from app.models.manager import ManagerPd, Manager
from app.schemas.managers import ManagerCreateModel

router = APIRouter(prefix="/api/v0/managers")


@router.post("/")
async def create_manager(data: ManagerCreateModel):
    data.password = hashpw(data.password.encode().replace(b"\x00", b""), gensalt()).decode()
    return await ManagerPd.from_tortoise_orm(await Manager.create(**data.model_dump()))
