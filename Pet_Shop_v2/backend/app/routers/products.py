from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.core.response import success
from app.models.user import User
from app.schemas.product import (
    CartAddRequest,
    CartUpdateRequest,
    ProductAuditRequest,
    ProductCreate,
    ProductUpdate,
)
from app.services.product_service import ProductService


router = APIRouter(tags=["products"])


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)) -> dict:
    categories = ProductService(db).list_categories()
    return success(categories)


@router.get("/products")
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, max_length=64),
    category_id: int | None = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    data = ProductService(db).list_public_products(
        page=page,
        page_size=page_size,
        keyword=keyword,
        category_id=category_id,
    )
    return success(data)


@router.get("/products/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    product = ProductService(db).get_public_product(product_id)
    return success(product)


@router.get("/cart")
def list_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    cart = ProductService(db).list_cart(current_user)
    return success(cart)


@router.post("/cart/items")
def add_cart_item(
    payload: CartAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    cart = ProductService(db).add_to_cart(current_user, payload)
    return success(cart)


@router.patch("/cart/items/{item_id}")
def update_cart_item(
    item_id: int,
    payload: CartUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    cart = ProductService(db).update_cart_item(current_user, item_id, payload)
    return success(cart)


@router.delete("/cart/items/{item_id}")
def delete_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    cart = ProductService(db).remove_cart_item(current_user, item_id)
    return success(cart)


@router.get("/merchant/products")
def list_merchant_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, max_length=64),
    status: str | None = Query(None, max_length=32),
    current_user: User = Depends(require_permission("product:manage")),
    db: Session = Depends(get_db),
) -> dict:
    data = ProductService(db).list_merchant_products(
        merchant=current_user,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )
    return success(data)


@router.post("/merchant/products")
def create_merchant_product(
    payload: ProductCreate,
    current_user: User = Depends(require_permission("product:manage")),
    db: Session = Depends(get_db),
) -> dict:
    product = ProductService(db).create_product(current_user, payload)
    return success(product)


@router.put("/merchant/products/{product_id}")
def update_merchant_product(
    product_id: int,
    payload: ProductUpdate,
    current_user: User = Depends(require_permission("product:manage")),
    db: Session = Depends(get_db),
) -> dict:
    product = ProductService(db).update_product(product_id, current_user, payload)
    return success(product)


@router.post("/merchant/products/{product_id}/submit")
def submit_merchant_product(
    product_id: int,
    current_user: User = Depends(require_permission("product:manage")),
    db: Session = Depends(get_db),
) -> dict:
    product = ProductService(db).submit_product(product_id, current_user)
    return success(product)


@router.post("/merchant/products/{product_id}/take-down")
def take_down_merchant_product(
    product_id: int,
    current_user: User = Depends(require_permission("product:manage")),
    db: Session = Depends(get_db),
) -> dict:
    product = ProductService(db).take_down_product(product_id, current_user)
    return success(product)


@router.get("/admin/products")
def list_audit_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, max_length=64),
    status: str | None = Query("pending", max_length=32),
    _: User = Depends(require_permission("product:audit")),
    db: Session = Depends(get_db),
) -> dict:
    data = ProductService(db).list_audit_products(
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
    )
    return success(data)


@router.post("/admin/products/{product_id}/approve")
def approve_product(
    product_id: int,
    payload: ProductAuditRequest,
    _: User = Depends(require_permission("product:audit")),
    db: Session = Depends(get_db),
) -> dict:
    product = ProductService(db).approve_product(product_id, payload.audit_note)
    return success(product)


@router.post("/admin/products/{product_id}/reject")
def reject_product(
    product_id: int,
    payload: ProductAuditRequest,
    _: User = Depends(require_permission("product:audit")),
    db: Session = Depends(get_db),
) -> dict:
    product = ProductService(db).reject_product(product_id, payload.audit_note)
    return success(product)
