from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.product import CartItem, Product, ProductCategory


class ProductRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_categories(self, only_enabled: bool = True) -> list[ProductCategory]:
        stmt = select(ProductCategory).order_by(ProductCategory.sort_order, ProductCategory.id)
        if only_enabled:
            stmt = stmt.where(ProductCategory.status == "enabled")
        return list(self.db.scalars(stmt))

    def get_category(self, category_id: int) -> Optional[ProductCategory]:
        return self.db.get(ProductCategory, category_id)

    def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        merchant_user_id: Optional[int] = None,
    ) -> tuple[list[Product], int]:
        stmt = select(Product)
        count_stmt = select(func.count()).select_from(Product)
        conditions = []

        if keyword:
            pattern = f"%{keyword}%"
            conditions.append(or_(Product.title.like(pattern), Product.subtitle.like(pattern)))
        if category_id:
            conditions.append(Product.category_id == category_id)
        if status:
            conditions.append(Product.status == status)
        if merchant_user_id:
            conditions.append(Product.merchant_user_id == merchant_user_id)

        for condition in conditions:
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        total = self.db.scalar(count_stmt) or 0
        products = list(
            self.db.scalars(
                stmt.order_by(Product.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return products, total

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.db.get(Product, product_id)

    def create_product(self, merchant_user_id: int, values: dict[str, Any]) -> Product:
        product = Product(merchant_user_id=merchant_user_id, status="pending", **values)
        self.db.add(product)
        self.db.flush()
        return product

    def update_product(self, product: Product, values: dict[str, Any]) -> Product:
        for key, value in values.items():
            setattr(product, key, value)
        self.db.flush()
        return product

    def get_cart_item(self, user_id: int, item_id: int) -> Optional[CartItem]:
        stmt = select(CartItem).where(CartItem.user_id == user_id, CartItem.id == item_id)
        return self.db.scalar(stmt)

    def get_cart_item_by_product(self, user_id: int, product_id: int) -> Optional[CartItem]:
        stmt = select(CartItem).where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
        )
        return self.db.scalar(stmt)

    def list_cart_items(self, user_id: int) -> list[CartItem]:
        stmt = select(CartItem).where(CartItem.user_id == user_id).order_by(CartItem.id.desc())
        return list(self.db.scalars(stmt))

    def add_cart_item(self, user_id: int, product_id: int, quantity: int) -> CartItem:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        self.db.add(cart_item)
        self.db.flush()
        return cart_item

    def delete_cart_item(self, cart_item: CartItem) -> None:
        self.db.delete(cart_item)
        self.db.flush()
