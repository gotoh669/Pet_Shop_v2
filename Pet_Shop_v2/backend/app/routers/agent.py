from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import oauth2_scheme
from app.core.exceptions import AppError
from app.core.response import success
from app.core.security import parse_access_token
from app.models.user import User
from app.schemas.agent import DeepSeekChatRequest, ShoppingGuideRequest
from app.services.deepseek_service import DeepSeekClient
from app.services.shopping_agent_service import ShoppingGuideAgent


router = APIRouter(prefix="/agent", tags=["agent"])


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if not token:
        return None
    try:
        payload = parse_access_token(token)
        user_id = int(payload.get("sub"))
    except (AppError, TypeError, ValueError):
        return None
    user = db.get(User, user_id)
    if not user or user.status != "active":
        return None
    return user


@router.post("/deepseek/chat")
def deepseek_chat(payload: DeepSeekChatRequest) -> dict:
    result = DeepSeekClient().simple_chat(
        message=payload.message,
        system_prompt=payload.system_prompt,
        model=payload.model,
        temperature=payload.temperature,
        max_tokens=payload.max_tokens,
    )
    return success(result)


@router.post("/shopping-guide")
def shopping_guide(
    payload: ShoppingGuideRequest,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> dict:
    result = ShoppingGuideAgent(db).recommend(
        payload=payload,
        user_id=current_user.id if current_user else None,
    )
    return success(result)
