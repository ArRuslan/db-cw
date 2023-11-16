from datetime import datetime, timedelta

from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app import models
from app.models._utils import Model


def dt():
    return datetime.now() - timedelta(days=6)


class Order(Model):
    id: int = fields.BigIntField(pk=True)
    status: str = fields.CharField(max_length=64)
    creation_time: datetime = fields.DatetimeField(default=dt)
    address: str = fields.TextField()
    type: str = fields.CharField(max_length=64)
    customer: models.Customer = fields.ForeignKeyField("models.Customer")
    manager: models.Manager = fields.ForeignKeyField("models.Manager")
    items = fields.ManyToManyField("models.Product", through="orderitem")

    class PydanticMeta:
        exclude = ["manager", "customer", "items"]


OrderPd = pydantic_model_creator(Order, name="OrderPd")
