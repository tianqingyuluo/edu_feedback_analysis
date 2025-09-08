"""
Celery 任务定义
定义分析任务的异步执行逻辑
"""

import pandas as pd
from typing import Dict, Any

from app.analysis.machine_learing.models.student_portrait import clean_input_data
from app.core.celery_app import celery_app
from app.core.logging import app_logger
from app.analysis.machine_learing.core.analysis_task_manager import AnalysisTaskManager
from app.db.database import db_manager
from app.db.models.analysis import AnalysisTask
from app.db.session import get_session
from app.enum.enums import AnalysisStatusEnum
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
import asyncio
import json

from app.service.data_clean_service import data_clean_task


@celery_app.task(bind=True)
def execute_analysis_task(self, task_id: int, data_id: int) -> Dict[str, Any]:
    """
    执行分析任务的 Celery 任务
    
    Args:
        task_id: 数据库中的任务ID
        data_id: 数据ID
        
    Returns:
        任务执行结果
    """
    app_logger.info(f"开始执行分析任务: task_id={task_id}, data_id={data_id}")
    
    try:
        # 获取数据库会话
        async def init_db():
            if not db_manager.engine:
                await db_manager.init()

        async def run_task():
            await init_db()
            async with get_session() as session:
                # 查询任务记录
                statement = select(AnalysisTask).where(AnalysisTask.id == task_id)
                result = await session.execute(statement)
                task = result.scalar_one_or_none()
                
                if not task:
                    raise ValueError(f"任务不存在: {task_id}")
                
                # 更新任务状态为运行中
                task.status = AnalysisStatusEnum.PROCESSING
                await session.commit()
                
                # 创建分析任务管理器
                task_manager = AnalysisTaskManager()
                task_manager.db = session
                
                # 加载数据（这里假设有一个方法可以根据data_id加载数据）
                # 实际实现中，你需要根据你的数据存储方式来实现这个方法
                data = await _load_data_by_id(task_id, data_id, session)
                
                if data is None:
                    raise ValueError(f"数据不存在: {data_id}")
                
                # 执行分析任务
                result = await task_manager.execute_analysis_task(
                    task_id=str(task_id),
                    data=data
                )
                
                # 更新任务状态
                if result.get("task_info", {}).get("status") == AnalysisStatusEnum.COMPLETED:
                    task.status = AnalysisStatusEnum.COMPLETED
                    task.summary = json.dumps(result, ensure_ascii=False)
                else:
                    task.status = AnalysisStatusEnum.FAILED
                    task.summary = json.dumps({
                        "error": result.get("error", "未知错误")
                    }, ensure_ascii=False)
                
                await session.commit()
                
                return result
        
        # 运行异步任务
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(run_task())
        finally:
            loop.close()
            
    except Exception as e:
        app_logger.error(f"执行分析任务失败: task_id={task_id}, error={str(e)}")
        
        # 更新任务状态为失败
        async def update_task_status():
            async with get_session() as session:
                statement = select(AnalysisTask).where(AnalysisTask.id == task_id)
                result = await session.execute(statement)
                task = result.scalar_one_or_none()
                
                if task:
                    task.status = AnalysisStatusEnum.FAILED
                    task.summary = json.dumps({"error": str(e)}, ensure_ascii=False)
                    await session.commit()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(update_task_status())
        finally:
            loop.close()
        
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e)
        }


async def _load_data_by_id(task_id: int, data_id: int, db: AsyncSession) -> pd.DataFrame:
    """
    根据数据ID加载数据
    
    Args:
        db: 数据库会话
        data_id: 数据ID
        task_id: 任务ID
        
    Returns:
        加载的数据DataFrame，如果不存在则返回None
    """
    df = await data_clean_task(task_id, data_id, db)

    return df


@celery_app.task
def check_and_execute_pending_tasks():
    """
    检查并执行待处理的任务
    这个任务可以定期执行，以确保没有遗漏的任务
    """
    app_logger.info("检查待执行的分析任务")
    
    async def check_tasks():
        async with get_session() as session:
            # 查询所有待处理的任务
            statement = select(AnalysisTask).where(
                AnalysisTask.status == AnalysisStatusEnum.PENDING
            )
            result = await session.execute(statement)
            pending_tasks = result.scalars().all()
            
            for task in pending_tasks:
                app_logger.info(f"发现待处理任务: {task.id}")
                # 提交执行任务
                execute_analysis_task.delay(task.id, task.data_id)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(check_tasks())
    finally:
        loop.close()