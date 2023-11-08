from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models._utils import Model


class Customer(Model):
    id: int = fields.BigIntField(pk=True)
    first_name: str = fields.CharField(max_length=128)
    last_name: str = fields.CharField(max_length=128)
    email: str = fields.CharField(max_length=256)
    phone_number: int = fields.BigIntField()


CustomerPd = pydantic_model_creator(Customer, name="CustomerPd")
