from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects import mysql

from app.core.database import Base


BigIntPk = BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")
BigIntFk = BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, unique=True)
    icon_url = Column(String(512), nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)
    status = Column(String(32), nullable=False, default="enabled")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Product(Base):
    __tablename__ = "products"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    merchant_user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(BigIntFk, ForeignKey("product_categories.id"), nullable=False, index=True)
    title = Column(String(160), nullable=False)
    subtitle = Column(String(255), nullable=True)
    brand = Column(String(64), nullable=True)
    cover_url = Column(String(512), nullable=True)
    image_urls = Column(JSON, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)
    stock = Column(Integer, nullable=False, default=0)
    sales_count = Column(Integer, nullable=False, default=0)
    spec = Column(String(128), nullable=True)
    applicable_pet = Column(String(64), nullable=True)
    tags = Column(JSON, nullable=True)
    detail = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    audit_note = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uk_cart_user_product"),
    )

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(BigIntFk, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    selected = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
