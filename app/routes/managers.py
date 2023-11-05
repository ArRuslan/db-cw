from bcrypt import hashpw, gensalt
from fastapi import APIRouter

from app.db import database
from app.schemas.managers import ManagerCreateModel

router = APIRouter(prefix="/api/v0/managers")


@router.post("/")
async def create_manager(data: ManagerCreateModel):
    data.password = hashpw(data.password.encode().replace(b"\x00", b""), gensalt()).decode()
    data = data.model_dump()
    return await database.fetch_one("INSERT INTO managers (first_name, last_name, email, password, permissions) "
                                    "VALUES (:first_name, :last_name, :email, :password, :permissions) "
                                    "RETURNING manager_id, first_name, last_name, email, permissions", data)
