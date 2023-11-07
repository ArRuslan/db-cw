from datetime import datetime
from typing import Optional

from pydantic import Field

from app.db import database
from app.models.base_model import Model
from app.models.customer import Customer
from app.models.product import Product


class Order(Model):
    id: int = Field(alias="order_id")
    status: str = Field(alias="order_status")
    creation_time: datetime = Field(alias="order_creation_time")
    address: str
    type: str = Field(alias="order_type")
    customer_id: int
    manager_id: int

    class Meta:
        table_name = "orders"
        sql_pk_name = "order_id"

        _full_sql = (
            "SELECT order_id, order_status, order_creation_time, address, order_type, manager_id, orders.customer_id, "
            "customers.first_name, customers.last_name, customers.email, customers.phone_number FROM orders "
            "INNER JOIN customers ON orders.customer_id=customers.customer_id")

    @classmethod
    async def get_full(cls, pk: int) -> Optional[dict]:
        result = await database.fetch_one(cls.Meta._full_sql + " WHERE order_id=:order_id", {"order_id": pk})
        return (cls(**result).model_dump()
                | {"customer": Customer(**result).model_dump()}
                | {"items": [i.model_dump(exclude={"per_order_limit"}) for i in await cls.items(pk)]})

    @classmethod
    async def fetch_full(cls, limit: int, offset: int) -> list[dict]:
        query = cls.Meta._full_sql + " LIMIT :limit OFFSET :offset;"
        return [(cls(**order).model_dump()
                | {"customer": Customer(**order).model_dump()}
                | {"items": [i.model_dump(exclude={"per_order_limit"}) for i in await cls.items(order["order_id"])]})
                for order in await database.fetch_all(query, {"limit": limit, "offset": offset})]

    @staticmethod
    async def items(pk: int) -> list[Product]:
        query = ("SELECT order_items.product_id, order_items.price_per_item AS price, order_items.quantity, model, "
                 "manufacturer, image_url, warranty_days, category_id, per_order_limit FROM order_items JOIN products "
                 "ON order_items.product_id=products.product_id WHERE order_id=:order_id;")

        return await Product.from_query(query, {"order_id": pk})
