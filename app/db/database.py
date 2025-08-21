from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.core.config import settings
from app.core.logging import app_logger


class DatabaseManager:
    """数据库管理器，负责创建和管理数据库引擎"""
    
    def __init__(self):
        self.engine: AsyncEngine | None = None
    
    async def init(self) -> None:
        """初始化数据库引擎"""
        try:
            # 构建数据库URL
            database_url = (
                f"postgresql+asyncpg://{settings.database_username}:{settings.database_password}@"
                f"{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
            )

            # 创建异步引擎
            self.engine = create_async_engine(
                database_url,
                echo=True,  # 回显上生产的时候要关掉
                future=True,
                pool_pre_ping=True,
                pool_recycle=300,
            )
            app_logger.info(f"数据库引擎已初始化: {database_url}")
        except Exception as e:
            app_logger.error(f"数据库引擎初始化失败: {e}")
            raise

    async def close(self) -> None:
        """关闭数据库引擎"""
        if self.engine:
            await self.engine.dispose()
    
    def get_engine(self) -> AsyncEngine:
        """获取数据库引擎"""
        if not self.engine:
            raise RuntimeError("数据库引擎未初始化")
        return self.engine

    async def check_connection(self) -> bool:
        """检查数据库连接是否正常"""
        if not self.engine:
            return False

        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            app_logger.error(f"数据库连接检查失败: {e}")
            return False


# 创建全局数据库管理器实例
db_manager = DatabaseManager()