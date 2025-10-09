from typing import AsyncGenerator
from fastapi import Depends
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import app_logger
from app.dependencies import get_db_session, get_rag_service
from app.schemas.question import Question
from app.service.rag_service import RAGService
from app.db.models.chat import ChatMessage, Chat

router = APIRouter()

# async def generate_stream_response(question: str, rag_service: RAGService) -> AsyncGenerator[str, None]:
#     async for token in rag_service.stream_query(question):
#         yield f"data:{token}\n\n"
#     yield "data: [DONE]\n\n"

async def generate_stream_response_with_storage(
    question: str,
    chat_id: int,
    rag_service: RAGService,
    db: AsyncSession,
    kb_id: int = None
) -> AsyncGenerator[str, None]:
    """
    生成流式响应并收集完整内容用于数据库存储
    """
    full_response = ""
    
    # 流式生成响应
    try:
        db_chat = await db.get(Chat, chat_id)
        if db_chat is None:
            app_logger.error(f"Chat {chat_id} not found")
            return

        # 添加用户消息到数据库
        user_message = ChatMessage(
            chatid=chat_id,
            role="user",
            content=question
        )
        db.add(user_message)
        await db.flush()
    except Exception as e:
        app_logger.error(f"保存用户消息到数据库失败: {e}")
        await db.rollback()

    async for token in rag_service.stream_query(question, kb_id):
        # 去除SSE格式标记，只保留实际内容
        clean_token = token.replace("data:", "").replace("\n\n", "")
        full_response += clean_token
        
        # 继续流式输出给客户端
        yield f"data:{token}\n\n"
    
    # 流式结束后，保存完整响应到数据库
    try:
        ai_message = ChatMessage(
            chatid=chat_id,
            role="assistant",
            content=full_response
        )
        db.add(ai_message)
        await db.commit()
    except Exception as e:
        # 记录错误但不影响流式响应
        app_logger.error(f"保存AI响应到数据库失败: {e}")
        await db.rollback()
    
    yield "data: [DONE]\n\n"

        
@router.post("/send/{chat_id}")
async def send(question: Question,
               chat_id: str,
               kb_id: int = None,
               rag_service: RAGService = Depends(get_rag_service),
               db: AsyncSession = Depends(get_db_session)):
    """
    发送问题并且返回llm的流式响应
    """
    return StreamingResponse(
        generate_stream_response_with_storage(question.question, int(chat_id), rag_service, db, kb_id),
        media_type="text/event-stream"
    )