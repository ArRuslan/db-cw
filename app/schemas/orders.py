from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.customers import CustomerModel


class ProductModel(BaseModel):
    id: int
    quantity: int = Field(ge=1)


class OrderCreateModel(BaseModel):
    customer_info: CustomerModel
    products: list[ProductModel]
    address: str
    type: str


class OrderUpdateModel(BaseModel):
    status: Optional[str] = None
    address: Optional[str] = None
    type: Optional[str] = None
