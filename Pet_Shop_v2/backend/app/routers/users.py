from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.models.user import User
from app.schemas.user import UserUpdate
from app.services.user_service import UserService, to_user_public


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)) -> dict:
    return success(to_user_public(current_user))


@router.put("/me")
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user = UserService(db).update_profile(current_user, payload)
    return success(user)


@router.patch("/me")
def patch_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user = UserService(db).update_profile(current_user, payload)
    return success(user)


@router.get("/me/roles")
def get_my_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    roles = UserService(db).get_roles(current_user)
    return success(roles)


@router.get("/me/permissions")
def get_my_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    permissions = UserService(db).get_permissions(current_user)
    return success(permissions)

