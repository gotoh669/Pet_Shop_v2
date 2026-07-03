from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    func,
)
from sqlalchemy.dialects import mysql

from app.core.database import Base


BigIntPk = BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")
BigIntFk = BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")


class User(Base):
    __tablename__ = "users"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    nickname = Column(String(64), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    gender = Column(String(16), nullable=False, default="unknown")
    city = Column(String(64), nullable=True)
    bio = Column(String(255), nullable=True)
    has_pet = Column(Boolean, nullable=False, default=False)
    pet_count = Column(Integer, nullable=False, default=0)
    interest_tags = Column(JSON, nullable=True)
    status = Column(String(32), nullable=False, default="active")
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class Role(Base):
    __tablename__ = "roles"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    code = Column(String(64), nullable=False, unique=True)
    name = Column(String(64), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    code = Column(String(96), nullable=False, unique=True)
    name = Column(String(96), nullable=False)
    module = Column(String(64), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(BigIntFk, ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(BigIntFk, ForeignKey("permissions.id"), primary_key=True)


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(BigIntFk, ForeignKey("users.id"), primary_key=True)
    role_id = Column(BigIntFk, ForeignKey("roles.id"), primary_key=True)
    merchant_id = Column(BigIntFk, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class SmsCode(Base):
    __tablename__ = "sms_codes"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    phone = Column(String(20), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    purpose = Column(String(32), nullable=False, default="login")
    status = Column(String(32), nullable=False, default="active")
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
