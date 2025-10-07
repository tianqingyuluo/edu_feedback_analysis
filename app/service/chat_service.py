from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.models import Chat, ChatMessage


class ChatService:
    """
    AI聊天服务
    """

    async def get_chat_room(self, task_id: str, user_id: str, db: AsyncSession) -> Chat:
        """
        获取聊天室
        """
        query = select(Chat).where(Chat.taskid == task_id, Chat.userid == user_id)
        result = await db.execute(query)
        chat_room = result.scalars().first()
        # 如果该聊天室不存在，则创建
        if not chat_room:
            chat_room = Chat(taskid=int(task_id), userid=int(user_id))
            db.add(chat_room)
            await db.commit()
            await db.refresh(chat_room)
        return chat_room

    async def get_chat_history(self, task_id: str, user_id: str, db: AsyncSession) -> list[ChatMessage]:
        """
        获取聊天记录
        """
        query = select(ChatMessage).where(ChatMessage.taskid == task_id, ChatMessage.userid == user_id)
        result = await db.execute(query)
        chat_history = result.scalars().all()
        return list(chat_history)