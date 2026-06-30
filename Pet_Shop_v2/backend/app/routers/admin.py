from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.core.response import success
from app.models.user import User
from app.schemas.user import UserRoleUpdate
from app.services.user_service import UserService


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, max_length=64),
    status: str | None = Query(None, max_length=32),
    _: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
) -> dict:
    data = UserService(db).list_users(
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )
    return success(data)


@router.get("/users/{user_id}")
def get_user_detail(
    user_id: int,
    _: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
) -> dict:
    user = UserService(db).get_user_detail(user_id)
    return success(user)


@router.post("/users/{user_id}/disable")
def disable_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
) -> dict:
    user = UserService(db).set_user_status(user_id, "disabled", current_user)
    return success(user)


@router.post("/users/{user_id}/enable")
def enable_user(
    user_id: int,
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
) -> dict:
    user = UserService(db).set_user_status(user_id, "active", current_user)
    return success(user)


@router.put("/users/{user_id}/roles")
def update_user_roles(
    user_id: int,
    payload: UserRoleUpdate,
    current_user: User = Depends(require_permission("user:manage")),
    db: Session = Depends(get_db),
) -> dict:
    user = UserService(db).update_user_roles(user_id, payload.role_codes, current_user)
    return success(user)
