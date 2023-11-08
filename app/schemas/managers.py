from pydantic import BaseModel

from app.utils import Permissions


class ManagerCreateModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    permissions: int = Permissions.DEFAULT
