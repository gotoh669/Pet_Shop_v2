from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects import mysql

from app.core.database import Base


BigIntPk = BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")
BigIntFk = BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql").with_variant(Integer, "sqlite")


class PetProfile(Base):
    __tablename__ = "pet_profiles"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(64), nullable=False)
    pet_type = Column(String(32), nullable=False)
    breed = Column(String(64), nullable=True)
    gender = Column(String(16), nullable=False, default="unknown")
    birthday = Column(Date, nullable=True)
    arrival_date = Column(Date, nullable=True)
    weight = Column(Numeric(6, 2), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    sterilized = Column(String(16), nullable=False, default="unknown")
    vaccine_status = Column(String(32), nullable=False, default="unknown")
    deworm_status = Column(String(32), nullable=False, default="unknown")
    health_notes = Column(Text, nullable=True)
    visibility = Column(String(32), nullable=False, default="private")
    source_type = Column(String(32), nullable=False, default="manual")
    source_live_pet_id = Column(BigIntFk, nullable=True)
    source_purchase_id = Column(BigIntFk, nullable=True)
    is_current = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class PetGrowthRecord(Base):
    __tablename__ = "pet_growth_records"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    pet_id = Column(BigIntFk, ForeignKey("pet_profiles.id"), nullable=False, index=True)
    user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    record_type = Column(String(32), nullable=False, default="daily")
    title = Column(String(128), nullable=False)
    content = Column(Text, nullable=True)
    media_urls = Column(JSON, nullable=True)
    weight = Column(Numeric(6, 2), nullable=True)
    record_date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class PetReminder(Base):
    __tablename__ = "pet_reminders"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    pet_id = Column(BigIntFk, ForeignKey("pet_profiles.id"), nullable=False, index=True)
    user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    reminder_type = Column(String(32), nullable=False)
    title = Column(String(128), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    repeat_rule = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
