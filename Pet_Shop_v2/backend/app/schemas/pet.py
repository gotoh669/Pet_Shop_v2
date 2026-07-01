from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field


class PetProfileBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    pet_type: str = Field(..., max_length=32)
    breed: Optional[str] = Field(None, max_length=64)
    gender: str = Field("unknown", max_length=16)
    birthday: Optional[date] = None
    arrival_date: Optional[date] = None
    weight: Optional[Decimal] = Field(None, ge=0)
    avatar_url: Optional[str] = Field(None, max_length=512)
    sterilized: str = Field("unknown", max_length=16)
    vaccine_status: str = Field("unknown", max_length=32)
    deworm_status: str = Field("unknown", max_length=32)
    health_notes: Optional[str] = None
    visibility: str = Field("private", max_length=32)
    source_type: str = Field("manual", max_length=32)
    source_live_pet_id: Optional[int] = None
    source_purchase_id: Optional[int] = None
    is_current: bool = False


class PetProfileCreate(PetProfileBase):
    pass


class PetProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    pet_type: Optional[str] = Field(None, max_length=32)
    breed: Optional[str] = Field(None, max_length=64)
    gender: Optional[str] = Field(None, max_length=16)
    birthday: Optional[date] = None
    arrival_date: Optional[date] = None
    weight: Optional[Decimal] = Field(None, ge=0)
    avatar_url: Optional[str] = Field(None, max_length=512)
    sterilized: Optional[str] = Field(None, max_length=16)
    vaccine_status: Optional[str] = Field(None, max_length=32)
    deworm_status: Optional[str] = Field(None, max_length=32)
    health_notes: Optional[str] = None
    visibility: Optional[str] = Field(None, max_length=32)
    is_current: Optional[bool] = None


class PetProfilePublic(PetProfileBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GrowthRecordCreate(BaseModel):
    record_type: str = Field("daily", max_length=32)
    title: str = Field(..., min_length=1, max_length=128)
    content: Optional[str] = None
    media_urls: Optional[Any] = None
    weight: Optional[Decimal] = Field(None, ge=0)
    record_date: date


class GrowthRecordPublic(GrowthRecordCreate):
    id: int
    pet_id: int
    user_id: int
    created_at: Optional[datetime] = None


class ReminderCreate(BaseModel):
    reminder_type: str = Field(..., max_length=32)
    title: str = Field(..., min_length=1, max_length=128)
    remind_at: datetime
    repeat_rule: Optional[str] = Field(None, max_length=64)


class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=128)
    remind_at: Optional[datetime] = None
    repeat_rule: Optional[str] = Field(None, max_length=64)
    status: Optional[str] = Field(None, max_length=32)


class ReminderPublic(ReminderCreate):
    id: int
    pet_id: int
    user_id: int
    status: str
    created_at: Optional[datetime] = None
