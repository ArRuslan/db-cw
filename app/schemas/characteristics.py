from typing import Optional

from pydantic import BaseModel


class CharCreateModel(BaseModel):
    name: str
    measurement_unit: str


class CharUpdateModel(BaseModel):
    name: Optional[str] = None
    measurement_unit: Optional[str] = None
