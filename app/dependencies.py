from fastapi import Depends
from collections.abc import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_session

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖函数"""
    async with get_session() as session:
        yield session