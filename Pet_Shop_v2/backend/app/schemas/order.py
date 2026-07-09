from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    cart_item_ids: Optional[list[int]] = None
    receiver_name: Optional[str] = Field(None, max_length=64)
    receiver_phone: Optional[str] = Field(None, max_length=20)
    receiver_address: Optional[str] = Field(None, max_length=255)
    remark: Optional[str] = None


class OrderItemPublic(BaseModel):
    id: int
    product_id: int
    merchant_user_id: int
    product_title: str
    product_cover_url: Optional[str] = None
    unit_price: Decimal
    quantity: int
    total_amount: Decimal


class OrderPublic(BaseModel):
    id: int
    order_no: str
    user_id: int
    merchant_user_id: int
    total_amount: Decimal
    status: str
    payment_status: str
    payment_method: Optional[str] = None
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    receiver_address: Optional[str] = None
    remark: Optional[str] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: list[OrderItemPublic] = []
