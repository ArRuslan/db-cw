from bcrypt import hashpw, gensalt
from fastapi import APIRouter, HTTPException

from app.models.manager import ManagerPd, Manager
from app.schemas.managers import ManagerCreateModel
from app.utils import AuthManagerDep, Permissions

router = APIRouter(prefix="/api/v0/managers")


@router.post("/")
async def create_manager(data: ManagerCreateModel, manager: AuthManagerDep):
    if not Permissions.check(manager, Permissions.ADMIN):
        raise HTTPException(status_code=403, detail="Insufficient privileges!")

    data.password = hashpw(data.password.encode().replace(b"\x00", b""), gensalt()).decode()
    return await ManagerPd.from_tortoise_orm(await Manager.create(**data.model_dump()))
