from uuid import uuid4

from tortoise import fields

from app import models
from app.models._utils import Model


class Session(Model):
    id: int = fields.BigIntField(pk=True)
    manager: models.Manager = fields.ForeignKeyField("models.Manager")
    token: str = fields.UUIDField(default=uuid4)
    