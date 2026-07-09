from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.core.response import success
from app.models.user import User
from app.schemas.order import OrderCreate
from app.services.order_service import OrderService


router = APIRouter(tags=["orders"])


@router.post("/orders")
def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = OrderService(db).create_order(current_user, payload)
    return success(order)


@router.get("/orders")
def list_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, max_length=32),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    data = OrderService(db).list_user_orders(current_user, page, page_size, status)
    return success(data)


@router.get("/orders/{order_id}")
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = OrderService(db).get_user_order(current_user, order_id)
    return success(order)


@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = OrderService(db).cancel_order(current_user, order_id)
    return success(order)


@router.post("/orders/{order_id}/mock-pay")
def mock_pay(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = OrderService(db).mock_pay(current_user, order_id)
    return success(order)


@router.post("/orders/{order_id}/confirm")
def confirm_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    order = OrderService(db).confirm_order(current_user, order_id)
    return success(order)


@router.get("/merchant/orders")
def list_merchant_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, max_length=32),
    current_user: User = Depends(require_permission("order:ship")),
    db: Session = Depends(get_db),
) -> dict:
    data = OrderService(db).list_merchant_orders(current_user, page, page_size, status)
    return success(data)


@router.post("/merchant/orders/{order_id}/ship")
def ship_order(
    order_id: int,
    current_user: User = Depends(require_permission("order:ship")),
    db: Session = Depends(get_db),
) -> dict:
    order = OrderService(db).ship_order(current_user, order_id)
    return success(order)


@router.get("/admin/orders")
def list_admin_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, max_length=32),
    _: User = Depends(require_permission("order:view")),
    db: Session = Depends(get_db),
) -> dict:
    data = OrderService(db).list_admin_orders(page, page_size, status)
    return success(data)
