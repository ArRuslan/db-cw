from pydantic import BaseModel


class ManagerCreateModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    permissions: int = 2
