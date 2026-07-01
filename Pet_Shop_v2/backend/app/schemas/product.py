from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field


class CategoryPublic(BaseModel):
    id: int
    name: str
    icon_url: Optional[str] = None
    sort_order: int
    status: str


class ProductBase(BaseModel):
    category_id: int
    title: str = Field(..., min_length=1, max_length=160)
    subtitle: Optional[str] = Field(None, max_length=255)
    brand: Optional[str] = Field(None, max_length=64)
    cover_url: Optional[str] = Field(None, max_length=512)
    image_urls: Optional[Any] = None
    price: Decimal = Field(..., ge=0)
    original_price: Optional[Decimal] = Field(None, ge=0)
    stock: int = Field(0, ge=0)
    spec: Optional[str] = Field(None, max_length=128)
    applicable_pet: Optional[str] = Field(None, max_length=64)
    tags: Optional[Any] = None
    detail: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=160)
    subtitle: Optional[str] = Field(None, max_length=255)
    brand: Optional[str] = Field(None, max_length=64)
    cover_url: Optional[str] = Field(None, max_length=512)
    image_urls: Optional[Any] = None
    price: Optional[Decimal] = Field(None, ge=0)
    original_price: Optional[Decimal] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    spec: Optional[str] = Field(None, max_length=128)
    applicable_pet: Optional[str] = Field(None, max_length=64)
    tags: Optional[Any] = None
    detail: Optional[str] = None


class ProductPublic(ProductBase):
    id: int
    merchant_user_id: int
    category_name: Optional[str] = None
    sales_count: int
    status: str
    audit_note: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProductAuditRequest(BaseModel):
    audit_note: Optional[str] = Field(None, max_length=255)


class CartAddRequest(BaseModel):
    product_id: int
    quantity: int = Field(1, ge=1, le=999)


class CartUpdateRequest(BaseModel):
    quantity: Optional[int] = Field(None, ge=1, le=999)
    selected: Optional[bool] = None


class CartItemPublic(BaseModel):
    id: int
    product_id: int
    quantity: int
    selected: bool
    product: ProductPublic


class CartSummary(BaseModel):
    items: list[CartItemPublic]
    total_quantity: int
    selected_quantity: int
    selected_amount: Decimal
