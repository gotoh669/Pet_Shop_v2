from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.order import Order, OrderItem
from app.models.product import CartItem
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.common import PageData
from app.schemas.order import OrderItemPublic, OrderPublic


def to_order_item_public(item: OrderItem) -> OrderItemPublic:
    return OrderItemPublic(
        id=item.id,
        product_id=item.product_id,
        merchant_user_id=item.merchant_user_id,
        product_title=item.product_title,
        product_cover_url=item.product_cover_url,
        unit_price=item.unit_price,
        quantity=item.quantity,
        total_amount=item.total_amount,
    )


def to_order_public(order: Order, items: list[OrderItem]) -> OrderPublic:
    return OrderPublic(
        id=order.id,
        order_no=order.order_no,
        user_id=order.user_id,
        merchant_user_id=order.merchant_user_id,
        total_amount=order.total_amount,
        status=order.status,
        payment_status=order.payment_status,
        payment_method=order.payment_method,
        receiver_name=order.receiver_name,
        receiver_phone=order.receiver_phone,
        receiver_address=order.receiver_address,
        remark=order.remark,
        paid_at=order.paid_at,
        shipped_at=order.shipped_at,
        completed_at=order.completed_at,
        cancelled_at=order.cancelled_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[to_order_item_public(item) for item in items],
    )


class OrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.orders = OrderRepository(db)
        self.products = ProductRepository(db)

    def create_order(self, user: User, payload: Any) -> OrderPublic:
        cart_items = self._selected_cart_items(user.id, getattr(payload, "cart_item_ids", None))
        if not cart_items:
            raise BadRequestError("No selected cart items")

        merchant_user_id: int | None = None
        total_amount = Decimal("0")
        order_lines: list[tuple[CartItem, Any, Decimal]] = []

        for cart_item in cart_items:
            product = self.products.get_product(cart_item.product_id)
            if not product or product.status != "active":
                raise BadRequestError("Cart contains unavailable product")
            if product.stock < cart_item.quantity:
                raise BadRequestError(f"Insufficient stock for product: {product.title}")
            if merchant_user_id is None:
                merchant_user_id = product.merchant_user_id
            elif merchant_user_id != product.merchant_user_id:
                raise BadRequestError("Please create separate orders for different merchants")
            line_amount = Decimal(str(product.price)) * cart_item.quantity
            total_amount += line_amount
            order_lines.append((cart_item, product, line_amount))

        order = Order(
            order_no=self._build_order_no(user.id),
            user_id=user.id,
            merchant_user_id=merchant_user_id,
            total_amount=total_amount,
            receiver_name=getattr(payload, "receiver_name", None),
            receiver_phone=getattr(payload, "receiver_phone", None),
            receiver_address=getattr(payload, "receiver_address", None),
            remark=getattr(payload, "remark", None),
        )
        self.orders.add_order(order)

        for cart_item, product, line_amount in order_lines:
            self.orders.add_item(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    merchant_user_id=product.merchant_user_id,
                    product_title=product.title,
                    product_cover_url=product.cover_url,
                    unit_price=product.price,
                    quantity=cart_item.quantity,
                    total_amount=line_amount,
                )
            )
            product.stock -= cart_item.quantity
            product.sales_count += cart_item.quantity
            self.products.delete_cart_item(cart_item)

        self.db.commit()
        self.db.refresh(order)
        return self.get_user_order(user, order.id)

    def list_user_orders(
        self,
        user: User,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> PageData:
        orders, total = self.orders.list_orders(
            page=page,
            page_size=page_size,
            user_id=user.id,
            status=status,
        )
        return self._page(orders, total, page, page_size)

    def get_user_order(self, user: User, order_id: int) -> OrderPublic:
        order = self._get_order(order_id)
        if order.user_id != user.id:
            raise ForbiddenError("Cannot access another user's order")
        return self._order_with_items(order)

    def cancel_order(self, user: User, order_id: int) -> OrderPublic:
        order = self._get_user_order_model(user, order_id)
        if order.status != "pending_payment":
            raise BadRequestError("Only pending payment orders can be cancelled")
        self._restore_stock(order)
        order.status = "cancelled"
        order.payment_status = "cancelled"
        order.cancelled_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        return self._order_with_items(order)

    def mock_pay(self, user: User, order_id: int) -> OrderPublic:
        order = self._get_user_order_model(user, order_id)
        if order.status != "pending_payment":
            raise BadRequestError("Only pending payment orders can be paid")
        order.status = "paid"
        order.payment_status = "paid"
        order.payment_method = "mock"
        order.paid_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        return self._order_with_items(order)

    def confirm_order(self, user: User, order_id: int) -> OrderPublic:
        order = self._get_user_order_model(user, order_id)
        if order.status != "shipped":
            raise BadRequestError("Only shipped orders can be confirmed")
        order.status = "completed"
        order.completed_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        return self._order_with_items(order)

    def list_merchant_orders(
        self,
        merchant: User,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> PageData:
        orders, total = self.orders.list_orders(
            page=page,
            page_size=page_size,
            merchant_user_id=merchant.id,
            status=status,
        )
        return self._page(orders, total, page, page_size)

    def ship_order(self, merchant: User, order_id: int) -> OrderPublic:
        order = self._get_order(order_id)
        if order.merchant_user_id != merchant.id:
            raise ForbiddenError("Cannot ship another merchant's order")
        if order.status != "paid":
            raise BadRequestError("Only paid orders can be shipped")
        order.status = "shipped"
        order.shipped_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(order)
        return self._order_with_items(order)

    def list_admin_orders(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> PageData:
        orders, total = self.orders.list_orders(page=page, page_size=page_size, status=status)
        return self._page(orders, total, page, page_size)

    def _selected_cart_items(self, user_id: int, cart_item_ids: list[int] | None) -> list[CartItem]:
        items = self.products.list_cart_items(user_id)
        if cart_item_ids:
            allowed = set(cart_item_ids)
            return [item for item in items if item.id in allowed]
        return [item for item in items if item.selected]

    def _build_order_no(self, user_id: int) -> str:
        return f"PS{datetime.utcnow():%Y%m%d%H%M%S%f}{user_id}"

    def _get_order(self, order_id: int) -> Order:
        order = self.orders.get_order(order_id)
        if not order:
            raise NotFoundError("Order not found")
        return order

    def _get_user_order_model(self, user: User, order_id: int) -> Order:
        order = self._get_order(order_id)
        if order.user_id != user.id:
            raise ForbiddenError("Cannot access another user's order")
        return order

    def _restore_stock(self, order: Order) -> None:
        for item in self.orders.get_items(order.id):
            product = self.products.get_product(item.product_id)
            if product:
                product.stock += item.quantity
                product.sales_count = max(0, product.sales_count - item.quantity)

    def _order_with_items(self, order: Order) -> OrderPublic:
        return to_order_public(order, self.orders.get_items(order.id))

    def _page(self, orders: list[Order], total: int, page: int, page_size: int) -> PageData:
        return PageData(
            items=[self._order_with_items(order) for order in orders],
            total=total,
            page=page,
            page_size=page_size,
        )
