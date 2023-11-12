from typing import Literal

from pydantic import BaseModel


class PaginationModel(BaseModel):
    page: int = 0
    pageSize: int = 10


class FilterItem(BaseModel):
    field: str
    operator: Literal[">", ">=", "=", "<=", "<", "contains", "between", "equals", "startsWith", "endsWith", "isEmpty",
                      "isNotEmpty", "isAnyOf", "!="]
    value: str | list[str] | None = None


class FilterModel(BaseModel):
    items: list[FilterItem]
    logicOperator: Literal["or", "and"]


class SortItem(BaseModel):
    field: str
    sort: Literal["asc", "desc"]


class SearchData(BaseModel):
    pagination: PaginationModel
    filter: FilterModel
    sort: list[SortItem]
