from sqlmodel.ext.asyncio.session import AsyncSession
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from app.db.database import db_manager

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的上下文管理器"""
    if not db_manager.engine:
        raise RuntimeError("数据库引擎未初始化")
    
    session = AsyncSession(db_manager.engine)
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

class DatabaseSessionManager:
    """数据库会话管理器"""
    
    @staticmethod
    @asynccontextmanager
    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话的上下文管理器"""
        if not db_manager.engine:
            raise RuntimeError("数据库引擎未初始化")
        
        session = AsyncSession(db_manager.engine)
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()