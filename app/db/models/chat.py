from sqlalchemy import BIGINT
from sqlmodel import Field
from .base import BaseModel



class Chat(BaseModel, table=True):
    """
    某次聊天，对应某次分析任务以及用户id
    """
    userid: int = Field(nullable=False, foreign_key="user.id", ondelete="CASCADE", index=True, sa_type=BIGINT)
    taskid: int = Field(nullable=False, foreign_key="analysistask.id", ondelete="CASCADE", index=True, sa_type=BIGINT)

class ChatMessage(BaseModel, table=True):
    """
    聊天消息
    """
    chatid: int = Field(nullable=False, foreign_key="chat.id", ondelete="CASCADE", index=True, sa_type=BIGINT)
    role: str = Field(nullable=False)
    content: str = Field(nullable=False)