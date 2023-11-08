from __future__ import annotations

from typing import Optional

from tortoise import fields

from app.models._utils import Model


class Category(Model):
    id: int = fields.BigIntField(pk=True)
    name: str = fields.CharField(max_length=200)
    description: Optional[str] = fields.TextField(null=True)
