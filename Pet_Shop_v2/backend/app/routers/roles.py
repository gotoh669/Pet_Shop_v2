from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.user_service import to_permission_public, to_role_public


router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("")
def list_roles(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    roles = [to_role_public(role) for role in UserRepository(db).list_roles()]
    return success(roles)


@router.get("/permissions")
def list_permissions(
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    permissions = [
        to_permission_public(permission)
        for permission in UserRepository(db).list_permissions()
    ]
    return success(permissions)
