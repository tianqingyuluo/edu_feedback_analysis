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
        # 修改查询方式
        statement = select(Chat).where(Chat.taskid == int(task_id), Chat.userid == int(user_id))
        result = await db.exec(statement)  # 使用 db.exec 而不是 db.execute
        chat_room = result.first()
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
        # 首先找到对应的聊天室
        chat_statement = select(Chat).where(Chat.taskid == int(task_id), Chat.userid == int(user_id))
        chat_result = await db.exec(chat_statement)
        chat_room = chat_result.first()
        
        if not chat_room:
            return []
        
        # 然后根据聊天室ID查找消息
        message_statement = select(ChatMessage).where(ChatMessage.chatid == chat_room.id)
        message_result = await db.exec(message_statement)
        chat_history = message_result.all()
        return list(chat_history)
