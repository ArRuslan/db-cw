from __future__ import annotations

from typing import Optional

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models._utils import Model


class Characteristic(Model):
    id: int = fields.BigIntField(pk=True)
    name: str = fields.CharField(max_length=255, unique=True)
    measurement_unit: Optional[str] = fields.CharField(max_length=32, null=True)


CharacteristicPd = pydantic_model_creator(Characteristic, name="CharacteristicPd")
