from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy import text
from sqlmodel import SQLModel
from app.db.database import db_manager
from app.core.logging import app_logger
from app.db.models import *  # 导入所有模型
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理器"""
    try:
        app_logger.info("启动数据库连接...")
        await db_manager.init()

        # 检查数据库连接
        if await db_manager.check_connection():
            app_logger.info("数据库连接成功")
            
            # 创建所有表（只创建不存在的表）
            app_logger.info("检查并创建数据库表...")
            engine = db_manager.get_engine()
            async with engine.begin() as conn:
                # 使用SQLModel创建所有表（如果不存在）
                await conn.run_sync(SQLModel.metadata.create_all)
            app_logger.info("数据库表初始化完成")
        else:
            app_logger.error("数据库连接失败")

        yield # 应用初始化结束，开始运行
    except Exception as e:
        app_logger.error(f"应用启动失败，错误信息：{e}")
    finally:
        app_logger.info("关闭数据库连接...")
        await db_manager.close()
        app_logger.info("应用安全关闭")