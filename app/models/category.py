from __future__ import annotations

from typing import Optional

from pydantic import Field

from app.models.base_model import Model


class Category(Model):
    id: int = Field(alias="category_id")
    name: str
    description: Optional[str]

    class Meta:
        table_name = "categories"
        sql_pk_name = "category_id"
