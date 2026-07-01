from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.product import CartItem, Product, ProductCategory
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.schemas.common import PageData
from app.schemas.product import (
    CartItemPublic,
    CartSummary,
    CategoryPublic,
    ProductPublic,
)


def _changes(payload: Any) -> dict[str, Any]:
    return payload.dict(exclude_unset=True)


def to_category_public(category: ProductCategory) -> CategoryPublic:
    return CategoryPublic(
        id=category.id,
        name=category.name,
        icon_url=category.icon_url,
        sort_order=category.sort_order,
        status=category.status,
    )


def to_product_public(product: Product, category: ProductCategory | None = None) -> ProductPublic:
    return ProductPublic(
        id=product.id,
        merchant_user_id=product.merchant_user_id,
        category_id=product.category_id,
        category_name=category.name if category else None,
        title=product.title,
        subtitle=product.subtitle,
        brand=product.brand,
        cover_url=product.cover_url,
        image_urls=product.image_urls,
        price=product.price,
        original_price=product.original_price,
        stock=product.stock,
        sales_count=product.sales_count,
        spec=product.spec,
        applicable_pet=product.applicable_pet,
        tags=product.tags,
        detail=product.detail,
        status=product.status,
        audit_note=product.audit_note,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


class ProductService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ProductRepository(db)

    def list_categories(self) -> list[CategoryPublic]:
        return [to_category_public(category) for category in self.repo.list_categories()]

    def list_public_products(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        category_id: int | None = None,
    ) -> PageData:
        products, total = self.repo.list_products(
            page=page,
            page_size=page_size,
            keyword=keyword,
            category_id=category_id,
            status="active",
        )
        return PageData(
            items=[self._product_with_category(product) for product in products],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_public_product(self, product_id: int) -> ProductPublic:
        product = self.repo.get_product(product_id)
        if not product or product.status != "active":
            raise NotFoundError("Product not found")
        return self._product_with_category(product)

    def list_merchant_products(
        self,
        merchant: User,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        status: str | None = None,
    ) -> PageData:
        products, total = self.repo.list_products(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status,
            merchant_user_id=merchant.id,
        )
        return PageData(
            items=[self._product_with_category(product) for product in products],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create_product(self, merchant: User, payload: Any) -> ProductPublic:
        values = _changes(payload)
        self._ensure_category(values.get("category_id"))
        product = self.repo.create_product(merchant.id, values)
        self.db.commit()
        self.db.refresh(product)
        return self._product_with_category(product)

    def update_product(self, product_id: int, merchant: User, payload: Any) -> ProductPublic:
        product = self._get_owned_product(product_id, merchant)
        if product.status == "active":
            raise BadRequestError("Active product must be taken down before editing")

        values = _changes(payload)
        if "category_id" in values:
            self._ensure_category(values["category_id"])
        if values:
            product = self.repo.update_product(product, values)
            product.status = "pending"
            product.audit_note = None
            self.db.commit()
            self.db.refresh(product)
        return self._product_with_category(product)

    def submit_product(self, product_id: int, merchant: User) -> ProductPublic:
        product = self._get_owned_product(product_id, merchant)
        if product.stock <= 0:
            raise BadRequestError("Product stock must be greater than 0")
        product.status = "pending"
        product.audit_note = None
        self.db.commit()
        self.db.refresh(product)
        return self._product_with_category(product)

    def take_down_product(self, product_id: int, merchant: User) -> ProductPublic:
        product = self._get_owned_product(product_id, merchant)
        product.status = "inactive"
        self.db.commit()
        self.db.refresh(product)
        return self._product_with_category(product)

    def list_audit_products(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        status: str | None = "pending",
    ) -> PageData:
        products, total = self.repo.list_products(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status,
        )
        return PageData(
            items=[self._product_with_category(product) for product in products],
            total=total,
            page=page,
            page_size=page_size,
        )

    def approve_product(self, product_id: int, audit_note: str | None = None) -> ProductPublic:
        product = self.repo.get_product(product_id)
        if not product:
            raise NotFoundError("Product not found")
        if product.stock <= 0:
            raise BadRequestError("Product stock must be greater than 0")
        product.status = "active"
        product.audit_note = audit_note
        self.db.commit()
        self.db.refresh(product)
        return self._product_with_category(product)

    def reject_product(self, product_id: int, audit_note: str | None = None) -> ProductPublic:
        product = self.repo.get_product(product_id)
        if not product:
            raise NotFoundError("Product not found")
        product.status = "rejected"
        product.audit_note = audit_note or "审核未通过"
        self.db.commit()
        self.db.refresh(product)
        return self._product_with_category(product)

    def list_cart(self, user: User) -> CartSummary:
        items = self.repo.list_cart_items(user.id)
        return self._cart_summary(items)

    def add_to_cart(self, user: User, payload: Any) -> CartSummary:
        product = self.repo.get_product(getattr(payload, "product_id"))
        if not product or product.status != "active":
            raise NotFoundError("Product not found")
        if product.stock <= 0:
            raise BadRequestError("Product is out of stock")

        quantity = int(getattr(payload, "quantity"))
        existing = self.repo.get_cart_item_by_product(user.id, product.id)
        if existing:
            existing.quantity = min(existing.quantity + quantity, product.stock)
        else:
            self.repo.add_cart_item(user.id, product.id, min(quantity, product.stock))
        self.db.commit()
        return self.list_cart(user)

    def update_cart_item(self, user: User, item_id: int, payload: Any) -> CartSummary:
        cart_item = self.repo.get_cart_item(user.id, item_id)
        if not cart_item:
            raise NotFoundError("Cart item not found")
        values = _changes(payload)
        if "quantity" in values:
            product = self.repo.get_product(cart_item.product_id)
            if not product:
                raise NotFoundError("Product not found")
            cart_item.quantity = min(values["quantity"], product.stock)
        if "selected" in values:
            cart_item.selected = values["selected"]
        self.db.commit()
        return self.list_cart(user)

    def remove_cart_item(self, user: User, item_id: int) -> CartSummary:
        cart_item = self.repo.get_cart_item(user.id, item_id)
        if not cart_item:
            raise NotFoundError("Cart item not found")
        self.repo.delete_cart_item(cart_item)
        self.db.commit()
        return self.list_cart(user)

    def _ensure_category(self, category_id: int | None) -> None:
        if not category_id or not self.repo.get_category(category_id):
            raise BadRequestError("Product category not found")

    def _get_owned_product(self, product_id: int, merchant: User) -> Product:
        product = self.repo.get_product(product_id)
        if not product:
            raise NotFoundError("Product not found")
        if product.merchant_user_id != merchant.id:
            raise ForbiddenError("Cannot manage another merchant's product")
        return product

    def _product_with_category(self, product: Product) -> ProductPublic:
        return to_product_public(product, self.repo.get_category(product.category_id))

    def _cart_summary(self, items: list[CartItem]) -> CartSummary:
        public_items = []
        selected_amount = Decimal("0")
        total_quantity = 0
        selected_quantity = 0

        for item in items:
            product = self.repo.get_product(item.product_id)
            if not product:
                continue
            public_item = CartItemPublic(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                selected=item.selected,
                product=self._product_with_category(product),
            )
            public_items.append(public_item)
            total_quantity += item.quantity
            if item.selected:
                selected_quantity += item.quantity
                selected_amount += Decimal(str(product.price)) * item.quantity

        return CartSummary(
            items=public_items,
            total_quantity=total_quantity,
            selected_quantity=selected_quantity,
            selected_amount=selected_amount,
        )
