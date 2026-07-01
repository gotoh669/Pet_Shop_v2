from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, func

from app.core.database import Base


BigIntPk = BigInteger().with_variant(Integer, "sqlite")
BigIntFk = BigInteger().with_variant(Integer, "sqlite")


class LivePet(Base):
    __tablename__ = "live_pets"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    merchant_user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    pet_code = Column(String(64), nullable=False, unique=True)
    display_name = Column(String(64), nullable=True)
    pet_type = Column(String(32), nullable=False)
    breed = Column(String(64), nullable=True)
    gender = Column(String(16), nullable=False, default="unknown")
    birthday = Column(Date, nullable=True)
    color = Column(String(64), nullable=True)
    weight = Column(Numeric(6, 2), nullable=True)
    city = Column(String(64), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    cover_url = Column(String(512), nullable=True)
    image_urls = Column(JSON, nullable=True)
    vaccine_info = Column(Text, nullable=True)
    deworm_info = Column(Text, nullable=True)
    health_certificate_url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    audit_note = Column(String(255), nullable=True)
    sold_to_user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=True)
    sold_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class LivePetPurchase(Base):
    __tablename__ = "live_pet_purchases"

    id = Column(BigIntPk, primary_key=True, autoincrement=True)
    live_pet_id = Column(BigIntFk, ForeignKey("live_pets.id"), nullable=False, index=True)
    user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    merchant_user_id = Column(BigIntFk, ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(32), nullable=False, default="completed")
    generated_pet_profile_id = Column(BigIntFk, ForeignKey("pet_profiles.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
