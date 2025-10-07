from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Chat
from app.dependencies import get_current_user, get_db_session
from app.service.chat_service import ChatService

router = APIRouter()

@router.get("/")
async def get_chat_room(
        task_id: str,
        user: User = Depends(get_current_user),
        chat_service: ChatService = Depends(ChatService),
        db: AsyncSession = Depends(get_db_session)):
    return await chat_service.get_chat_room(task_id, str(user.id), db)
