from typing import Optional

from pydantic import Field

from app.models.base_model import Model


class Product(Model):
    id: int = Field(alias="product_id")
    model: str
    manufacturer: str
    price: float
    quantity: int
    per_order_limit: Optional[int]
    image_url: Optional[str]
    warranty_days: int
    category_id: int

    class Meta:
        table_name = "products"
        sql_pk_name = "product_id"
