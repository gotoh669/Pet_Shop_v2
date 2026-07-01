from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pet import PetGrowthRecord, PetProfile, PetReminder


class PetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_pets(self, user_id: int) -> list[PetProfile]:
        stmt = select(PetProfile).where(PetProfile.user_id == user_id).order_by(PetProfile.is_current.desc(), PetProfile.id.desc())
        return list(self.db.scalars(stmt))

    def get_pet(self, user_id: int, pet_id: int) -> Optional[PetProfile]:
        stmt = select(PetProfile).where(PetProfile.user_id == user_id, PetProfile.id == pet_id)
        return self.db.scalar(stmt)

    def get_current_pet(self, user_id: int) -> Optional[PetProfile]:
        stmt = select(PetProfile).where(PetProfile.user_id == user_id, PetProfile.is_current == True)
        return self.db.scalar(stmt)

    def create_pet(self, user_id: int, values: dict[str, Any]) -> PetProfile:
        pet = PetProfile(user_id=user_id, **values)
        self.db.add(pet)
        self.db.flush()
        return pet

    def update_pet(self, pet: PetProfile, values: dict[str, Any]) -> PetProfile:
        for key, value in values.items():
            setattr(pet, key, value)
        self.db.flush()
        return pet

    def clear_current_pet(self, user_id: int) -> None:
        for pet in self.list_pets(user_id):
            pet.is_current = False
        self.db.flush()

    def list_records(self, user_id: int, pet_id: int) -> list[PetGrowthRecord]:
        stmt = (
            select(PetGrowthRecord)
            .where(PetGrowthRecord.user_id == user_id, PetGrowthRecord.pet_id == pet_id)
            .order_by(PetGrowthRecord.record_date.desc(), PetGrowthRecord.id.desc())
        )
        return list(self.db.scalars(stmt))

    def create_record(self, user_id: int, pet_id: int, values: dict[str, Any]) -> PetGrowthRecord:
        record = PetGrowthRecord(user_id=user_id, pet_id=pet_id, **values)
        self.db.add(record)
        self.db.flush()
        return record

    def list_reminders(self, user_id: int, pet_id: int) -> list[PetReminder]:
        stmt = (
            select(PetReminder)
            .where(PetReminder.user_id == user_id, PetReminder.pet_id == pet_id)
            .order_by(PetReminder.status, PetReminder.remind_at)
        )
        return list(self.db.scalars(stmt))

    def get_reminder(self, user_id: int, reminder_id: int) -> Optional[PetReminder]:
        stmt = select(PetReminder).where(PetReminder.user_id == user_id, PetReminder.id == reminder_id)
        return self.db.scalar(stmt)

    def create_reminder(self, user_id: int, pet_id: int, values: dict[str, Any]) -> PetReminder:
        reminder = PetReminder(user_id=user_id, pet_id=pet_id, status="active", **values)
        self.db.add(reminder)
        self.db.flush()
        return reminder
