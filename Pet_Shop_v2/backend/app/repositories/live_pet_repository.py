from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.live_pet import LivePet, LivePetPurchase


class LivePetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_live_pets(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        pet_type: Optional[str] = None,
        status: Optional[str] = None,
        merchant_user_id: Optional[int] = None,
    ) -> tuple[list[LivePet], int]:
        stmt = select(LivePet)
        count_stmt = select(func.count()).select_from(LivePet)
        conditions = []
        if keyword:
            pattern = f"%{keyword}%"
            conditions.append(or_(LivePet.display_name.like(pattern), LivePet.breed.like(pattern), LivePet.pet_code.like(pattern)))
        if pet_type:
            conditions.append(LivePet.pet_type == pet_type)
        if status:
            conditions.append(LivePet.status == status)
        if merchant_user_id:
            conditions.append(LivePet.merchant_user_id == merchant_user_id)

        for condition in conditions:
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        total = self.db.scalar(count_stmt) or 0
        items = list(
            self.db.scalars(
                stmt.order_by(LivePet.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return items, total

    def get_live_pet(self, live_pet_id: int) -> Optional[LivePet]:
        return self.db.get(LivePet, live_pet_id)

    def create_live_pet(self, merchant_user_id: int, values: dict[str, Any]) -> LivePet:
        live_pet = LivePet(merchant_user_id=merchant_user_id, status="pending", **values)
        self.db.add(live_pet)
        self.db.flush()
        return live_pet

    def update_live_pet(self, live_pet: LivePet, values: dict[str, Any]) -> LivePet:
        for key, value in values.items():
            setattr(live_pet, key, value)
        self.db.flush()
        return live_pet

    def create_purchase(
        self,
        live_pet_id: int,
        user_id: int,
        merchant_user_id: int,
        amount: object,
    ) -> LivePetPurchase:
        purchase = LivePetPurchase(
            live_pet_id=live_pet_id,
            user_id=user_id,
            merchant_user_id=merchant_user_id,
            amount=amount,
            status="completed",
        )
        self.db.add(purchase)
        self.db.flush()
        return purchase
