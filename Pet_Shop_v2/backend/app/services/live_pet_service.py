from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, ForbiddenError, NotFoundError
from app.models.live_pet import LivePet, LivePetPurchase
from app.models.pet import PetProfile
from app.models.user import User
from app.repositories.live_pet_repository import LivePetRepository
from app.repositories.pet_repository import PetRepository
from app.schemas.common import PageData
from app.schemas.live_pet import LivePetPublic, LivePetPurchasePublic
from app.services.pet_service import to_pet_public


def _changes(payload: Any) -> dict[str, Any]:
    return payload.dict(exclude_unset=True)


def to_live_pet_public(live_pet: LivePet) -> LivePetPublic:
    return LivePetPublic(
        id=live_pet.id,
        merchant_user_id=live_pet.merchant_user_id,
        pet_code=live_pet.pet_code,
        display_name=live_pet.display_name,
        pet_type=live_pet.pet_type,
        breed=live_pet.breed,
        gender=live_pet.gender,
        birthday=live_pet.birthday,
        color=live_pet.color,
        weight=live_pet.weight,
        city=live_pet.city,
        price=live_pet.price,
        cover_url=live_pet.cover_url,
        image_urls=live_pet.image_urls,
        vaccine_info=live_pet.vaccine_info,
        deworm_info=live_pet.deworm_info,
        health_certificate_url=live_pet.health_certificate_url,
        description=live_pet.description,
        status=live_pet.status,
        audit_note=live_pet.audit_note,
        sold_to_user_id=live_pet.sold_to_user_id,
        sold_at=live_pet.sold_at,
        created_at=live_pet.created_at,
        updated_at=live_pet.updated_at,
    )


class LivePetService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = LivePetRepository(db)
        self.pet_repo = PetRepository(db)

    def list_public_live_pets(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        pet_type: str | None = None,
    ) -> PageData:
        items, total = self.repo.list_live_pets(
            page=page,
            page_size=page_size,
            keyword=keyword,
            pet_type=pet_type,
            status="active",
        )
        return PageData(
            items=[to_live_pet_public(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_public_live_pet(self, live_pet_id: int) -> LivePetPublic:
        live_pet = self.repo.get_live_pet(live_pet_id)
        if not live_pet or live_pet.status != "active":
            raise NotFoundError("Live pet not found")
        return to_live_pet_public(live_pet)

    def list_merchant_live_pets(
        self,
        merchant: User,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        status: str | None = None,
    ) -> PageData:
        items, total = self.repo.list_live_pets(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status,
            merchant_user_id=merchant.id,
        )
        return PageData(
            items=[to_live_pet_public(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create_live_pet(self, merchant: User, payload: Any) -> LivePetPublic:
        values = _changes(payload)
        self._validate(values)
        live_pet = self.repo.create_live_pet(merchant.id, values)
        self.db.commit()
        self.db.refresh(live_pet)
        return to_live_pet_public(live_pet)

    def update_live_pet(self, live_pet_id: int, merchant: User, payload: Any) -> LivePetPublic:
        live_pet = self._get_owned_live_pet(live_pet_id, merchant)
        if live_pet.status == "sold":
            raise BadRequestError("Sold live pet cannot be edited")
        values = _changes(payload)
        if values:
            self._validate(values, partial=True)
            live_pet = self.repo.update_live_pet(live_pet, values)
            live_pet.status = "pending"
            live_pet.audit_note = None
            self.db.commit()
            self.db.refresh(live_pet)
        return to_live_pet_public(live_pet)

    def take_down_live_pet(self, live_pet_id: int, merchant: User) -> LivePetPublic:
        live_pet = self._get_owned_live_pet(live_pet_id, merchant)
        if live_pet.status == "sold":
            raise BadRequestError("Sold live pet cannot be taken down")
        live_pet.status = "inactive"
        self.db.commit()
        self.db.refresh(live_pet)
        return to_live_pet_public(live_pet)

    def list_audit_live_pets(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str | None = None,
        status: str | None = "pending",
    ) -> PageData:
        items, total = self.repo.list_live_pets(
            page=page,
            page_size=page_size,
            keyword=keyword,
            status=status,
        )
        return PageData(
            items=[to_live_pet_public(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def approve_live_pet(self, live_pet_id: int, audit_note: str | None = None) -> LivePetPublic:
        live_pet = self.repo.get_live_pet(live_pet_id)
        if not live_pet:
            raise NotFoundError("Live pet not found")
        if live_pet.status == "sold":
            raise BadRequestError("Sold live pet cannot be approved")
        live_pet.status = "active"
        live_pet.audit_note = audit_note
        self.db.commit()
        self.db.refresh(live_pet)
        return to_live_pet_public(live_pet)

    def reject_live_pet(self, live_pet_id: int, audit_note: str | None = None) -> LivePetPublic:
        live_pet = self.repo.get_live_pet(live_pet_id)
        if not live_pet:
            raise NotFoundError("Live pet not found")
        live_pet.status = "rejected"
        live_pet.audit_note = audit_note or "审核未通过"
        self.db.commit()
        self.db.refresh(live_pet)
        return to_live_pet_public(live_pet)

    def purchase_live_pet(self, user: User, live_pet_id: int) -> LivePetPurchasePublic:
        live_pet = self.repo.get_live_pet(live_pet_id)
        if not live_pet or live_pet.status != "active":
            raise NotFoundError("Live pet not found")
        if live_pet.merchant_user_id == user.id:
            raise BadRequestError("Cannot buy your own live pet")

        purchase = self.repo.create_purchase(
            live_pet_id=live_pet.id,
            user_id=user.id,
            merchant_user_id=live_pet.merchant_user_id,
            amount=live_pet.price,
        )
        self.pet_repo.clear_current_pet(user.id)
        pet = PetProfile(
            user_id=user.id,
            name=live_pet.display_name or live_pet.pet_code,
            pet_type=live_pet.pet_type,
            breed=live_pet.breed,
            gender=live_pet.gender,
            birthday=live_pet.birthday,
            weight=live_pet.weight,
            avatar_url=live_pet.cover_url,
            vaccine_status="completed" if live_pet.vaccine_info else "unknown",
            deworm_status="completed" if live_pet.deworm_info else "unknown",
            health_notes=live_pet.description,
            visibility="private",
            source_type="purchase",
            source_live_pet_id=live_pet.id,
            source_purchase_id=purchase.id,
            is_current=True,
        )
        self.db.add(pet)
        self.db.flush()
        purchase.generated_pet_profile_id = pet.id
        live_pet.status = "sold"
        live_pet.sold_to_user_id = user.id
        live_pet.sold_at = datetime.utcnow()
        user.has_pet = True
        user.pet_count = len(self.pet_repo.list_pets(user.id))
        self.db.commit()
        self.db.refresh(purchase)
        self.db.refresh(pet)
        return LivePetPurchasePublic(
            id=purchase.id,
            live_pet_id=purchase.live_pet_id,
            user_id=purchase.user_id,
            merchant_user_id=purchase.merchant_user_id,
            amount=purchase.amount,
            status=purchase.status,
            generated_pet_profile_id=purchase.generated_pet_profile_id,
            generated_pet=to_pet_public(pet),
            created_at=purchase.created_at,
        )

    def _get_owned_live_pet(self, live_pet_id: int, merchant: User) -> LivePet:
        live_pet = self.repo.get_live_pet(live_pet_id)
        if not live_pet:
            raise NotFoundError("Live pet not found")
        if live_pet.merchant_user_id != merchant.id:
            raise ForbiddenError("Cannot manage another merchant's live pet")
        return live_pet

    def _validate(self, values: dict[str, Any], partial: bool = False) -> None:
        if not partial and not values.get("pet_code"):
            raise BadRequestError("Pet code is required")
        if not partial and not values.get("pet_type"):
            raise BadRequestError("Pet type is required")
        if not partial and values.get("price") is None:
            raise BadRequestError("Price is required")
