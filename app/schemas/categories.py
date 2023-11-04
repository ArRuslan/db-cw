from typing import Optional

from pydantic import BaseModel


class CategoryCreateModel(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryUpdateModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
