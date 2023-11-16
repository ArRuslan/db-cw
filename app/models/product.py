from typing import Optional

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app import models
from app.models._utils import Model


class Product(Model):
    id: int = fields.BigIntField(pk=True)
    model: str = fields.CharField(max_length=128)
    manufacturer: str = fields.CharField(max_length=128)
    price: float = fields.FloatField(default=0)
    quantity: int = fields.IntField(default=0)
    per_order_limit: int = fields.IntField(default=0)
    image_url: Optional[str] = fields.TextField(null=True)
    warranty_days: int = fields.IntField(default=0)
    category: models.Category | None = fields.ForeignKeyField("models.Category", null=True, default=None)
    characteristics = fields.ManyToManyField("models.Characteristic", through="productcharacteristic")

    class PydanticMeta:
        exclude = ["category", "characteristics"]


ProductPd = pydantic_model_creator(Product, name="ProductPd")
