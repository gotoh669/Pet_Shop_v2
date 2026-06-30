from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    id: int
    phone: Optional[str] = None
    nickname: str
    avatar_url: Optional[str] = None
    gender: str
    city: Optional[str] = None
    bio: Optional[str] = None
    has_pet: bool
    pet_count: int
    interest_tags: Optional[Any] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, min_length=1, max_length=64)
    avatar_url: Optional[str] = Field(None, max_length=512)
    gender: Optional[str] = Field(None, max_length=16)
    city: Optional[str] = Field(None, max_length=64)
    bio: Optional[str] = Field(None, max_length=255)
    has_pet: Optional[bool] = None
    pet_count: Optional[int] = Field(None, ge=0)
    interest_tags: Optional[Any] = None


class RolePublic(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str] = None


class UserAdminPublic(UserPublic):
    roles: list[RolePublic] = Field(default_factory=list)
    last_login_at: Optional[datetime] = None


class PermissionPublic(BaseModel):
    id: int
    code: str
    name: str
    module: str


class UserListQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    keyword: Optional[str] = Field(None, max_length=64)
    status: Optional[str] = Field(None, max_length=32)


class UserRoleUpdate(BaseModel):
    role_codes: list[str] = Field(..., min_length=1)
