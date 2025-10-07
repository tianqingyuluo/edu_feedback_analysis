from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Chat
from app.dependencies import get_current_user, get_db_session
from app.exception.exceptions.base import AppException
from app.service.chat_service import ChatService

router = APIRouter()

@router.get("/history/{chat_id}")
async def get_history(
        chat_id: str,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session)):
    chat_room = await db.get(Chat, int(chat_id))
    if chat_room is None:
        raise AppException("聊天室不存在", "404")
    if chat_room.userid != user.id:
        raise AppException("无权限访问", "403")
    return await ChatService().get_chat_history(str(chat_room.taskid), str(user.id), db)