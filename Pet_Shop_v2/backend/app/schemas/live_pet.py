from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.pet import PetProfilePublic


class LivePetBase(BaseModel):
    pet_code: str = Field(..., min_length=1, max_length=64)
    display_name: Optional[str] = Field(None, max_length=64)
    pet_type: str = Field(..., max_length=32)
    breed: Optional[str] = Field(None, max_length=64)
    gender: str = Field("unknown", max_length=16)
    birthday: Optional[date] = None
    color: Optional[str] = Field(None, max_length=64)
    weight: Optional[Decimal] = Field(None, ge=0)
    city: Optional[str] = Field(None, max_length=64)
    price: Decimal = Field(..., ge=0)
    cover_url: Optional[str] = Field(None, max_length=512)
    image_urls: Optional[Any] = None
    vaccine_info: Optional[str] = None
    deworm_info: Optional[str] = None
    health_certificate_url: Optional[str] = Field(None, max_length=512)
    description: Optional[str] = None


class LivePetCreate(LivePetBase):
    pass


class LivePetUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=64)
    pet_type: Optional[str] = Field(None, max_length=32)
    breed: Optional[str] = Field(None, max_length=64)
    gender: Optional[str] = Field(None, max_length=16)
    birthday: Optional[date] = None
    color: Optional[str] = Field(None, max_length=64)
    weight: Optional[Decimal] = Field(None, ge=0)
    city: Optional[str] = Field(None, max_length=64)
    price: Optional[Decimal] = Field(None, ge=0)
    cover_url: Optional[str] = Field(None, max_length=512)
    image_urls: Optional[Any] = None
    vaccine_info: Optional[str] = None
    deworm_info: Optional[str] = None
    health_certificate_url: Optional[str] = Field(None, max_length=512)
    description: Optional[str] = None


class LivePetPublic(LivePetBase):
    id: int
    merchant_user_id: int
    status: str
    audit_note: Optional[str] = None
    sold_to_user_id: Optional[int] = None
    sold_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class LivePetPurchasePublic(BaseModel):
    id: int
    live_pet_id: int
    user_id: int
    merchant_user_id: int
    amount: Decimal
    status: str
    generated_pet_profile_id: Optional[int] = None
    generated_pet: Optional[PetProfilePublic] = None
    created_at: Optional[datetime] = None


class LivePetAuditRequest(BaseModel):
    audit_note: Optional[str] = Field(None, max_length=255)
