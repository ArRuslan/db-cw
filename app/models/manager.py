from pydantic import Field

from app.models.base_model import Model


class Manager(Model):
    id: int = Field(alias="manager_id")
    first_name: str
    last_name: str
    email: str
    password: str
    permissions: int

    class Meta:
        table_name = "managers"
        sql_pk_name = "manager_id"
