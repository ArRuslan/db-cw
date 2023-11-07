from typing import Optional

from pydantic import BaseModel


class ProductCreateModel(BaseModel):
    model: str
    manufacturer: str
    price: float
    quantity: int = 0
    per_order_limit: Optional[int] = None
    image_url: Optional[str] = None
    warranty_days: int = 14
    category_id: int


class ProductUpdateModel(BaseModel):
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    per_order_limit: Optional[int] = None
    image_url: Optional[str] = None
    warranty_days: Optional[int] = None
    category_id: Optional[int] = None
