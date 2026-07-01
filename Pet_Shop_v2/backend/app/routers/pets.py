from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.models.user import User
from app.schemas.pet import (
    GrowthRecordCreate,
    PetProfileCreate,
    PetProfileUpdate,
    ReminderCreate,
    ReminderUpdate,
)
from app.services.pet_service import PetService


router = APIRouter(prefix="/pets", tags=["pets"])


@router.get("")
def list_pets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    pets = PetService(db).list_pets(current_user)
    return success(pets)


@router.post("")
def create_pet(
    payload: PetProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    pet = PetService(db).create_pet(current_user, payload)
    return success(pet)


@router.get("/current")
def get_current_pet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    pet = PetService(db).get_current_pet(current_user)
    return success(pet)


@router.get("/{pet_id}")
def get_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    pet = PetService(db).get_pet(current_user, pet_id)
    return success(pet)


@router.put("/{pet_id}")
def update_pet(
    pet_id: int,
    payload: PetProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    pet = PetService(db).update_pet(current_user, pet_id, payload)
    return success(pet)


@router.post("/{pet_id}/current")
def set_current_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    pet = PetService(db).set_current_pet(current_user, pet_id)
    return success(pet)


@router.get("/{pet_id}/records")
def list_records(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    records = PetService(db).list_records(current_user, pet_id)
    return success(records)


@router.post("/{pet_id}/records")
def create_record(
    pet_id: int,
    payload: GrowthRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    record = PetService(db).create_record(current_user, pet_id, payload)
    return success(record)


@router.get("/{pet_id}/reminders")
def list_reminders(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    reminders = PetService(db).list_reminders(current_user, pet_id)
    return success(reminders)


@router.post("/{pet_id}/reminders")
def create_reminder(
    pet_id: int,
    payload: ReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    reminder = PetService(db).create_reminder(current_user, pet_id, payload)
    return success(reminder)


@router.patch("/reminders/{reminder_id}")
def update_reminder(
    reminder_id: int,
    payload: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    reminder = PetService(db).update_reminder(current_user, reminder_id, payload)
    return success(reminder)
