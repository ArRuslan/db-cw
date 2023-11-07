from pydantic import Field

from app.models.base_model import Model


class OrderItem(Model):
    id: int = Field(alias="orderitem_id")
    order_id: int
    product_id: int
    quantity: int
    price: float = Field(alias="price_per_item")

    class Meta:
        table_name = "order_items"
        sql_pk_name = "orderitem_id"
