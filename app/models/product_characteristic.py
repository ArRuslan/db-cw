from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

from app import models
from app.models._utils import Model


class ProductCharacteristic(Model):
    id: int = fields.BigIntField(pk=True)
    product: models.Product = fields.ForeignKeyField("models.Product")
    characteristic: models.Characteristic = fields.ForeignKeyField("models.Characteristic")
    value: str = fields.TextField()

    class PydanticMeta:
        exclude = ["id", "product", "characteristic"]


ProductCharacteristicPd = pydantic_model_creator(ProductCharacteristic, name="ProductCharacteristicPd")
