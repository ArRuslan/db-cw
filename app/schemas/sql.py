from pydantic import BaseModel


class ExecuteSql(BaseModel):
    query: str
