from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.pet import PetGrowthRecord, PetProfile, PetReminder
from app.models.user import User
from app.repositories.pet_repository import PetRepository
from app.schemas.pet import GrowthRecordPublic, PetProfilePublic, ReminderPublic


def _changes(payload: Any) -> dict[str, Any]:
    return payload.dict(exclude_unset=True)


def to_pet_public(pet: PetProfile) -> PetProfilePublic:
    return PetProfilePublic(
        id=pet.id,
        user_id=pet.user_id,
        name=pet.name,
        pet_type=pet.pet_type,
        breed=pet.breed,
        gender=pet.gender,
        birthday=pet.birthday,
        arrival_date=pet.arrival_date,
        weight=pet.weight,
        avatar_url=pet.avatar_url,
        sterilized=pet.sterilized,
        vaccine_status=pet.vaccine_status,
        deworm_status=pet.deworm_status,
        health_notes=pet.health_notes,
        visibility=pet.visibility,
        source_type=pet.source_type,
        source_live_pet_id=pet.source_live_pet_id,
        source_purchase_id=pet.source_purchase_id,
        is_current=bool(pet.is_current),
        created_at=pet.created_at,
        updated_at=pet.updated_at,
    )


def to_record_public(record: PetGrowthRecord) -> GrowthRecordPublic:
    return GrowthRecordPublic(
        id=record.id,
        pet_id=record.pet_id,
        user_id=record.user_id,
        record_type=record.record_type,
        title=record.title,
        content=record.content,
        media_urls=record.media_urls,
        weight=record.weight,
        record_date=record.record_date,
        created_at=record.created_at,
    )


def to_reminder_public(reminder: PetReminder) -> ReminderPublic:
    return ReminderPublic(
        id=reminder.id,
        pet_id=reminder.pet_id,
        user_id=reminder.user_id,
        reminder_type=reminder.reminder_type,
        title=reminder.title,
        remind_at=reminder.remind_at,
        repeat_rule=reminder.repeat_rule,
        status=reminder.status,
        created_at=reminder.created_at,
    )


class PetService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PetRepository(db)

    def list_pets(self, user: User) -> list[PetProfilePublic]:
        return [to_pet_public(pet) for pet in self.repo.list_pets(user.id)]

    def get_current_pet(self, user: User) -> PetProfilePublic | None:
        pet = self.repo.get_current_pet(user.id)
        return to_pet_public(pet) if pet else None

    def get_pet(self, user: User, pet_id: int) -> PetProfilePublic:
        return to_pet_public(self._get_pet(user, pet_id))

    def create_pet(self, user: User, payload: Any) -> PetProfilePublic:
        values = _changes(payload)
        self._validate_pet(values)
        if values.get("is_current") or not self.repo.list_pets(user.id):
            self.repo.clear_current_pet(user.id)
            values["is_current"] = True
        pet = self.repo.create_pet(user.id, values)
        self._sync_user_pet_stats(user)
        self.db.commit()
        self.db.refresh(pet)
        return to_pet_public(pet)

    def update_pet(self, user: User, pet_id: int, payload: Any) -> PetProfilePublic:
        pet = self._get_pet(user, pet_id)
        values = _changes(payload)
        self._validate_pet(values, partial=True)
        if values.get("is_current"):
            self.repo.clear_current_pet(user.id)
        pet = self.repo.update_pet(pet, values)
        self._sync_user_pet_stats(user)
        self.db.commit()
        self.db.refresh(pet)
        return to_pet_public(pet)

    def set_current_pet(self, user: User, pet_id: int) -> PetProfilePublic:
        pet = self._get_pet(user, pet_id)
        self.repo.clear_current_pet(user.id)
        pet.is_current = True
        self.db.commit()
        self.db.refresh(pet)
        return to_pet_public(pet)

    def list_records(self, user: User, pet_id: int) -> list[GrowthRecordPublic]:
        self._get_pet(user, pet_id)
        return [to_record_public(record) for record in self.repo.list_records(user.id, pet_id)]

    def create_record(self, user: User, pet_id: int, payload: Any) -> GrowthRecordPublic:
        pet = self._get_pet(user, pet_id)
        values = _changes(payload)
        record = self.repo.create_record(user.id, pet.id, values)
        if values.get("weight") is not None:
            pet.weight = values["weight"]
        self.db.commit()
        self.db.refresh(record)
        return to_record_public(record)

    def list_reminders(self, user: User, pet_id: int) -> list[ReminderPublic]:
        self._get_pet(user, pet_id)
        return [to_reminder_public(reminder) for reminder in self.repo.list_reminders(user.id, pet_id)]

    def create_reminder(self, user: User, pet_id: int, payload: Any) -> ReminderPublic:
        pet = self._get_pet(user, pet_id)
        reminder = self.repo.create_reminder(user.id, pet.id, _changes(payload))
        self.db.commit()
        self.db.refresh(reminder)
        return to_reminder_public(reminder)

    def update_reminder(self, user: User, reminder_id: int, payload: Any) -> ReminderPublic:
        reminder = self.repo.get_reminder(user.id, reminder_id)
        if not reminder:
            raise NotFoundError("Reminder not found")
        values = _changes(payload)
        for key, value in values.items():
            setattr(reminder, key, value)
        self.db.commit()
        self.db.refresh(reminder)
        return to_reminder_public(reminder)

    def _get_pet(self, user: User, pet_id: int) -> PetProfile:
        pet = self.repo.get_pet(user.id, pet_id)
        if not pet:
            raise NotFoundError("Pet not found")
        return pet

    def _validate_pet(self, values: dict[str, Any], partial: bool = False) -> None:
        if not partial and not values.get("name"):
            raise BadRequestError("Pet name is required")

    def _sync_user_pet_stats(self, user: User) -> None:
        pets = self.repo.list_pets(user.id)
        user.has_pet = bool(pets)
        user.pet_count = len(pets)
        self.db.flush()
