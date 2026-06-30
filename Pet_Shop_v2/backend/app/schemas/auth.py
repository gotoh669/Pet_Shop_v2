from pydantic import BaseModel, Field

from app.schemas.user import UserPublic


class SmsSendRequest(BaseModel):
    phone: str = Field(..., min_length=5, max_length=20)


class SmsSendResponse(BaseModel):
    phone: str
    code: str
    expires_in: int


class SmsLoginRequest(BaseModel):
    phone: str = Field(..., min_length=5, max_length=20)
    code: str = Field(..., min_length=4, max_length=10)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic
