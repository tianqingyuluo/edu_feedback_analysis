from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from app.db.database import db_manager
from app.core.logging import app_logger
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理器"""
    try:
        app_logger.info("启动数据库连接...")
        await db_manager.init()

        # 检查数据库连接
        if await db_manager.check_connection():
            app_logger.info("数据库连接成功")
        else:
            app_logger.error("数据库连接失败")

        yield # 应用初始化结束，开始运行
    except Exception as e:
        app_logger.error(f"应用启动失败，错误信息：{e}")
    finally:
        app_logger.info("关闭数据库连接...")
        await db_manager.close()
        app_logger.info("应用安全关闭")