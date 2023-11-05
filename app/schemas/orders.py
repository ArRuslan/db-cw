from pydantic import BaseModel, Field


class CostumerInfoModel(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: int


class ProductModel(BaseModel):
    id: int
    quantity: int = Field(ge=1)


class OrderCreateModel(BaseModel):
    customer_info: CostumerInfoModel
    products: list[ProductModel]
    address: str
    type: str
