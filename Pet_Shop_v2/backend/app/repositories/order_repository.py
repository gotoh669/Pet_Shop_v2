from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem


class OrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_orders(
        self,
        page: int = 1,
        page_size: int = 20,
        user_id: Optional[int] = None,
        merchant_user_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> tuple[list[Order], int]:
        stmt = select(Order)
        count_stmt = select(func.count()).select_from(Order)
        conditions = []
        if user_id:
            conditions.append(Order.user_id == user_id)
        if merchant_user_id:
            conditions.append(Order.merchant_user_id == merchant_user_id)
        if status:
            conditions.append(Order.status == status)
        for condition in conditions:
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)
        total = self.db.scalar(count_stmt) or 0
        orders = list(
            self.db.scalars(
                stmt.order_by(Order.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return orders, total

    def get_order(self, order_id: int) -> Optional[Order]:
        return self.db.get(Order, order_id)

    def get_items(self, order_id: int) -> list[OrderItem]:
        stmt = select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.id)
        return list(self.db.scalars(stmt))

    def add_order(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order

    def add_item(self, item: OrderItem) -> OrderItem:
        self.db.add(item)
        self.db.flush()
        return item
