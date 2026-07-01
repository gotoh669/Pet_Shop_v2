from datetime import datetime, timedelta
import secrets

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import BadRequestError, UnauthorizedError
from app.core.security import create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth import SmsSendResponse, TokenResponse
from app.services.sms_service import SmsSender
from app.services.user_service import to_user_public


def _normalize_phone(phone: str) -> str:
    return phone.strip()


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = UserRepository(db)

    def send_sms_code(self, payload: object) -> SmsSendResponse:
        phone = _normalize_phone(getattr(payload, "phone"))
        if not phone:
            raise BadRequestError("Phone is required")

        code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = datetime.utcnow() + timedelta(minutes=settings.sms_code_expire_minutes)
        self.repo.expire_active_sms_codes(phone)
        self.repo.create_sms_code(phone=phone, code=code, expires_at=expires_at)
        result = SmsSender().send_login_code(
            phone=phone,
            code=code,
            expire_minutes=settings.sms_code_expire_minutes,
        )
        self.db.commit()
        return SmsSendResponse(
            phone=phone,
            code=code if result.provider == "mock" or settings.sms_debug_return_code else None,
            expires_in=settings.sms_code_expire_minutes * 60,
            provider=result.provider,
            sent=result.sent,
        )

    def sms_login(self, payload: object) -> TokenResponse:
        phone = _normalize_phone(getattr(payload, "phone"))
        code = str(getattr(payload, "code")).strip()
        sms_code = self.repo.get_latest_active_sms_code(phone)
        if not sms_code:
            raise UnauthorizedError("Sms code not found")
        if sms_code.expires_at < datetime.utcnow():
            sms_code.status = "expired"
            self.db.flush()
            self.db.commit()
            raise UnauthorizedError("Sms code expired")
        if sms_code.code != code:
            raise UnauthorizedError("Invalid sms code")

        user = self.repo.get_user_by_phone(phone)
        if not user:
            user = self.repo.create_user(phone=phone, nickname=f"user_{phone[-4:]}")
            self.repo.grant_role_if_exists(user.id, "user")
        elif user.status != "active":
            raise UnauthorizedError("User is not active")

        sms_code.status = "used"
        sms_code.used_at = datetime.utcnow()
        user.last_login_at = datetime.utcnow()
        self.db.flush()
        self.db.commit()
        self.db.refresh(user)
        return self._build_token_response(user)

    def _build_token_response(self, user: object) -> TokenResponse:
        token = create_access_token(str(getattr(user, "id")))
        return TokenResponse(
            access_token=token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=to_user_public(user),
        )
