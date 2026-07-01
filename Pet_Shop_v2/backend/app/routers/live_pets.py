from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.core.response import success
from app.models.user import User
from app.schemas.live_pet import LivePetAuditRequest, LivePetCreate, LivePetUpdate
from app.services.live_pet_service import LivePetService


router = APIRouter(tags=["live_pets"])


@router.get("/live-pets")
def list_live_pets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, max_length=64),
    pet_type: str | None = Query(None, max_length=32),
    db: Session = Depends(get_db),
) -> dict:
    data = LivePetService(db).list_public_live_pets(
        page=page,
        page_size=page_size,
        keyword=keyword,
        pet_type=pet_type,
    )
    return success(data)


@router.get("/live-pets/{live_pet_id}")
def get_live_pet(live_pet_id: int, db: Session = Depends(get_db)) -> dict:
    live_pet = LivePetService(db).get_public_live_pet(live_pet_id)
    return success(live_pet)


@router.post("/live-pets/{live_pet_id}/purchase")
def purchase_live_pet(
    live_pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    purchase = LivePetService(db).purchase_live_pet(current_user, live_pet_id)
    return success(purchase)


@router.get("/merchant/live-pets")
def list_merchant_live_pets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, max_length=64),
    status: str | None = Query(None, max_length=32),
    current_user: User = Depends(require_permission("product:manage")),
    db: Session = Depends(get_db),
) -> dict:
    data = LivePetService(db).list_merchant_live_pets(
        merchant=current_user,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )
    return success(data)


@router.post("/merchant/live-pets")
def create_merchant_live_pet(
    payload: LivePetCreate,
    current_user: User = Depends(require_permission("product:manage")),
    db: Session = Depends(get_db),
) -> dict:
    live_pet = LivePetService(db).create_live_pet(current_user, payload)
    return success(live_pet)


@router.put("/merchant/live-pets/{live_pet_id}")
def update_merchant_live_pet(
    live_pet_id: int,
    payload: LivePetUpdate,
    current_user: User = Depends(require_permission("product:manage")),
    db: Session = Depends(get_db),
) -> dict:
    live_pet = LivePetService(db).update_live_pet(live_pet_id, current_user, payload)
    return success(live_pet)


@router.post("/merchant/live-pets/{live_pet_id}/take-down")
def take_down_merchant_live_pet(
    live_pet_id: int,
    current_user: User = Depends(require_permission("product:manage")),
    db: Session = Depends(get_db),
) -> dict:
    live_pet = LivePetService(db).take_down_live_pet(live_pet_id, current_user)
    return success(live_pet)


@router.get("/admin/live-pets")
def list_audit_live_pets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, max_length=64),
    status: str | None = Query("pending", max_length=32),
    _: User = Depends(require_permission("product:audit")),
    db: Session = Depends(get_db),
) -> dict:
    data = LivePetService(db).list_audit_live_pets(
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )
    return success(data)


@router.post("/admin/live-pets/{live_pet_id}/approve")
def approve_live_pet(
    live_pet_id: int,
    payload: LivePetAuditRequest,
    _: User = Depends(require_permission("product:audit")),
    db: Session = Depends(get_db),
) -> dict:
    live_pet = LivePetService(db).approve_live_pet(live_pet_id, payload.audit_note)
    return success(live_pet)


@router.post("/admin/live-pets/{live_pet_id}/reject")
def reject_live_pet(
    live_pet_id: int,
    payload: LivePetAuditRequest,
    _: User = Depends(require_permission("product:audit")),
    db: Session = Depends(get_db),
) -> dict:
    live_pet = LivePetService(db).reject_live_pet(live_pet_id, payload.audit_note)
    return success(live_pet)
