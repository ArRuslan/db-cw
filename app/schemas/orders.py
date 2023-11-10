from typing import Optional, Literal

from pydantic import BaseModel, Field

from app.schemas.customers import CustomerModel


class ProductModel(BaseModel):
    id: int
    quantity: int = Field(ge=1)


class OrderCreateModel(BaseModel):
    customer_info: CustomerModel
    products: list[ProductModel]
    address: str
    type: Literal["shipping", "pickup"]


class OrderUpdateModel(BaseModel):
    status: Optional[str] = None
    address: Optional[str] = None
    type: Optional[str] = None
