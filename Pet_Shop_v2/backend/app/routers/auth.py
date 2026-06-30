from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.response import success
from app.schemas.auth import SmsLoginRequest, SmsSendRequest
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sms/send")
def send_sms_code(payload: SmsSendRequest, db: Session = Depends(get_db)) -> dict:
    sms_code = AuthService(db).send_sms_code(payload)
    return success(sms_code)


@router.post("/sms/login")
def sms_login(payload: SmsLoginRequest, db: Session = Depends(get_db)) -> dict:
    token = AuthService(db).sms_login(payload)
    return success(token)
