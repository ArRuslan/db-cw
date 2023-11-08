from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app import models
from app.models._utils import Model


class OrderItem(Model):
    id: int = fields.BigIntField(pk=True)
    order: models.Order = fields.ForeignKeyField("models.Order")
    product: models.Product = fields.ForeignKeyField("models.Product")
    quantity: int = fields.IntField()
    price: float = fields.FloatField()

    class PydanticMeta:
        exclude = ["order", "product"]


OrderItemPd = pydantic_model_creator(OrderItem, name="OrderItemPd")
