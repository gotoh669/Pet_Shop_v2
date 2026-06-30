from typing import Any

from pydantic import BaseModel, Field


class PageData(BaseModel):
    items: list[Any]
    total: int
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
