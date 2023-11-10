from datetime import datetime

from tortoise import fields

from app import models
from app.models._utils import Model


class Return(Model):
    id: int = fields.BigIntField(pk=True)
    status: str = fields.CharField(max_length=128, default="processing")
    creation_time: datetime = fields.DatetimeField(default=datetime.now)
    quantity: int = fields.IntField()
    reason: str = fields.TextField(null=True, default=None)
    order: models.Order = fields.ForeignKeyField("models.Order")
    order_item: models.OrderItem = fields.ForeignKeyField("models.OrderItem")
