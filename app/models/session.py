from pydantic import Field

from app.models.base_model import Model


class Session(Model):
    id: int = Field(alias="session_id")
    manager_id: int
    token: str

    class Meta:
        table_name = "sessions"
        sql_pk_name = "session_id"
