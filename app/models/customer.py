from pydantic import Field

from app.models.base_model import Model


class Customer(Model):
    id: int = Field(alias="customer_id")
    first_name: str
    last_name: str
    email: str
    phone_number: int

    class Meta:
        table_name = "customers"
        sql_pk_name = "customer_id"
