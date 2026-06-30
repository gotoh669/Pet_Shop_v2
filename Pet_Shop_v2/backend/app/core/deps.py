from collections.abc import Callable
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import parse_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.api_prefix}/auth/sms/login",
    auto_error=False,
)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise UnauthorizedError()

    payload = parse_access_token(token)
    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError("Invalid token subject")

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid token subject") from exc

    user = db.get(User, user_id)
    if not user:
        raise UnauthorizedError("User not found")
    if user.status != "active":
        raise ForbiddenError("User is not active")
    return user


def require_permission(permission_code: str) -> Callable[..., User]:
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        permissions = UserRepository(db).get_user_permission_codes(current_user.id)
        if permission_code not in permissions:
            raise ForbiddenError(f"Missing permission: {permission_code}")
        return current_user

    return dependency


def require_role(role_code: str) -> Callable[..., User]:
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        roles = UserRepository(db).get_user_role_codes(current_user.id)
        if role_code not in roles:
            raise ForbiddenError(f"Missing role: {role_code}")
        return current_user

    return dependency
