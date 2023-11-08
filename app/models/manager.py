from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models._utils import Model


class Manager(Model):
    id: int = fields.BigIntField(pk=True)
    first_name: str = fields.CharField(max_length=128)
    last_name: str = fields.CharField(max_length=128)
    email: str = fields.CharField(max_length=256)
    password: str = fields.CharField(max_length=256)
    permissions: int = fields.IntField(default=2)

    class PydanticMeta:
        exclude = ["password"]


ManagerPd = pydantic_model_creator(Manager, name="ManagerPd")
