from fastapi import APIRouter, Depends

from app.db.models import User
from app.dependencies import get_current_user
from app.schemas import UserRead

router = APIRouter()

@router.get("")
async def get_me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)