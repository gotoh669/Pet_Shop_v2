from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class DeepSeekChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    system_prompt: str = Field("You are a helpful assistant.", max_length=1000)
    model: Optional[str] = Field(None, max_length=64)
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(512, ge=1, le=4096)


class DeepSeekChatResponse(BaseModel):
    model: str
    content: str
    usage: Optional[dict] = None


class ShoppingGuideRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=500)
    budget: Optional[Decimal] = Field(None, ge=0)
    pet_type: Optional[str] = Field(None, max_length=32)
    breed: Optional[str] = Field(None, max_length=64)


class ShoppingGuideProduct(BaseModel):
    id: int
    title: str
    price: Decimal
    cover_url: Optional[str] = None
    category_name: Optional[str] = None
    stock: int
    reason: str


class ShoppingGuideResponse(BaseModel):
    summary: str
    advice: list[str]
    products: list[ShoppingGuideProduct]
    source: str
