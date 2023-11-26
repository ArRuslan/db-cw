from typing import Optional

from pydantic import BaseModel


class ReturnCreateModel(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    reason: Optional[str] = None


class ReturnUpdateModel(BaseModel):
    quantity: int
    reason: Optional[str] = None
