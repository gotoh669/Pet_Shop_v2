from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func

from app.core.database import Base


BigIntPk = BigInteger().with_variant(Integer, "sqlite")
BigIntFk = BigInteger().with_variant(Integer, "sqlite")


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    order_no = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    merchant_user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(32), nullable=False, default="pending_payment")
    payment_status = Column(String(32), nullable=False, default="unpaid")
    payment_method = Column(String(32), nullable=True)
    receiver_name = Column(String(64), nullable=True)
    receiver_phone = Column(String(20), nullable=True)
    receiver_address = Column(String(255), nullable=True)
    remark = Column(Text, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    shipped_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    order_id = Column(BigIntFk, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(BigIntFk, ForeignKey("products.id"), nullable=False, index=True)
    merchant_user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    product_title = Column(String(160), nullable=False)
    product_cover_url = Column(String(512), nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
