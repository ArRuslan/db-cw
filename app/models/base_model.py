from __future__ import annotations

from abc import ABC
from typing import Any, Optional, Union

from pydantic import BaseModel

from app.db import database


class Model(BaseModel, ABC):
    class Meta:
        table_name = ""
        sql_pk_name = ""

    def model_dump(self, **kwargs) -> dict[str, Any]:
        kwargs["by_alias"] = False
        return super().model_dump(**kwargs)

    @classmethod
    async def count(cls) -> int:
        res = await database.fetch_one(f"SELECT COUNT(*) as count FROM {cls.Meta.table_name};")
        return res["count"]

    @classmethod
    async def fetch(cls, limit: int, offset: int) -> list[Model]:
        if limit == 0:
            limit = await cls.count() + 1
        query = f"SELECT * FROM {cls.Meta.table_name} LIMIT :limit OFFSET :offset;"
        result = await database.fetch_all(query, {"limit": limit, "offset": offset})
        return [cls(**row) for row in result]

    @classmethod
    async def get_or_none(cls, pk: int) -> Optional[Model]:
        result = await database.fetch_one(f"SELECT * FROM {cls.Meta.table_name} WHERE {cls.Meta.sql_pk_name}=:id;",
                                          {"id": pk})
        if result is not None:
            return cls(**result)

    @classmethod
    async def delete(cls, pk: int) -> None:
        await database.execute(f"DELETE FROM {cls.Meta.table_name} WHERE {cls.Meta.sql_pk_name}=:id;", {"id": pk})

    @classmethod
    async def from_query(cls, query: str, values: dict, *, many: bool=True) -> Union[list[Model], Model]:
        result = await (database.fetch_all(query, values) if many else database.fetch_one(query, values))
        if many:
            return [cls(**row) for row in result]
        return cls(**result)
