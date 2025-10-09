"""
分析任务服务
提供分析任务的创建、执行和管理功能
"""

import pandas as pd
from typing import Dict, List, Any

from app.core.logging import app_logger
from app.analysis.machine_learing.core.analysis_task_manager import AnalysisTaskManager
from app.analysis.machine_learing.tasks.celery_tasks import execute_analysis_task
from app.db.models.analysis import AnalysisTask
from app.enum.enums import AnalysisStatusEnum
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select


class AnalysisService:
    """分析任务服务类"""
    
    def __init__(self):
        self.task_manager = AnalysisTaskManager()
    
    async def create_and_queue_analysis_task(
        self,
        session: AsyncSession,
        data_id: int,
        models_to_train: List[str] = None,
        analyses_to_run: List[str] = None,
        target_column: str = "学校整体满意度",
        feature_score_threshold: float = 0.16,
    ) -> AnalysisTask:
        """
        创建分析任务并将其加入队列
        
        Args:
            session: 数据库会话
            data_id: 数据ID
            models_to_train: 要训练的模型列表
            analyses_to_run: 要运行的统计分析列表
            target_column: 目标列名（仅what_if模型需要）
            feature_score_threshold: 特征选择分数阈值
            description: 任务描述
            
        Returns:
            创建的分析任务对象
        """
        app_logger.info(f"创建分析任务: data_id={data_id}")

        self.task_manager.db = session
        
        # 创建分析任务记录
        task = await self.task_manager.create_analysis_task(
            data_id=data_id,
            models_to_train=models_to_train,
            analyses_to_run=analyses_to_run,
            target_column=target_column,
            feature_score_threshold=feature_score_threshold,
            db=session
        )
        
        # 保存任务到数据库
        session.add(task)
        await session.commit()
        await session.refresh(task)
        
        # 将任务加入队列
        execute_analysis_task.delay(task.id, data_id)
        
        app_logger.info(f"分析任务已创建并加入队列: task_id={task.id}")
        return task
    
    async def get_task_status(self, session: AsyncSession, task_id: int) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            session: 数据库会话
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        statement = select(AnalysisTask).where(AnalysisTask.id == task_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        
        return {
            "task_id": task.id,
            "data_id": task.data_id,
            "status": task.status,
            "summary": task.summary,
            "created_at": task.created_at,
        }
    
    async def get_task_results(self, session: AsyncSession, task_id: int) -> Dict[str, Any]:
        """
        获取任务结果
        
        Args:
            session: 数据库会话
            task_id: 任务ID
            
        Returns:
            任务结果
        """
        # 首先检查任务状态
        task_status = await self.get_task_status(session, task_id)
        
        if task_status["status"] != AnalysisStatusEnum.COMPLETED:
            return {
                "task_id": task_id,
                "status": task_status["status"],
                "message": "任务尚未完成",
            }
        
        # 从文件系统加载结果
        try:
            return self.task_manager.get_task_results(str(task_id))
        except FileNotFoundError:
            return {
                "task_id": task_id,
                "status": task_status["status"],
                "error": "结果文件不存在",
            }
    
    async def generate_comprehensive_analysis(
        self,
        session: AsyncSession,
        task_id: int,
        input_data: pd.DataFrame = None,
        model_versions: Dict[str, int] = None,
    ) -> Dict[str, Any]:
        """
        生成综合分析报告
        
        Args:
            session: 数据库会话
            task_id: 任务ID
            input_data: 输入数据（用于模型预测）
            model_versions: 指定模型版本
            
        Returns:
            综合分析结果
        """
        # 检查任务是否存在且已完成
        task_status = await self.get_task_status(session, task_id)
        
        if task_status["status"] != AnalysisStatusEnum.COMPLETED:
            raise ValueError(f"任务未完成，无法生成综合分析报告: {task_id}")
        
        # 生成综合分析报告
        return await self.task_manager.generate_comprehensive_analysis(
            task_id=str(task_id),
            db=session,
            # input_data=input_data,
            model_versions=model_versions,
        )
    
    async def list_tasks(
        self,
        session: AsyncSession,
        limit: int = 10,
        offset: int = 0,
        status: str = None,
    ) -> Dict[str, Any]:
        """
        列出分析任务
        
        Args:
            session: 数据库会话
            limit: 限制返回数量
            offset: 偏移量
            status: 状态筛选
            
        Returns:
            任务列表和总数
        """
        # 构建查询
        statement = select(AnalysisTask)
        
        if status:
            statement = statement.where(AnalysisTask.status == status)
        
        # 获取总数
        count_statement = select(AnalysisTask)
        if status:
            count_statement = count_statement.where(AnalysisTask.status == status)
        
        count_result = await session.execute(count_statement)
        total = len(count_result.scalars().all())
        
        # 应用分页
        statement = statement.offset(offset).limit(limit).order_by(AnalysisTask.created_at.desc())
        result = await session.execute(statement)
        tasks = result.scalars().all()
        
        # 转换为字典格式
        task_list = []
        for task in tasks:
            task_list.append({
                "task_id": task.id,
                "data_id": task.data_id,
                "status": task.status,
                "summary": task.summary,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
            })
        
        return {
            "tasks": task_list,
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    
    async def cancel_task(self, session: AsyncSession, task_id: int) -> bool:
        """
        取消任务
        
        Args:
            session: 数据库会话
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        statement = select(AnalysisTask).where(AnalysisTask.id == task_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        
        # 只有待处理或运行中的任务可以取消
        if task.status in [AnalysisStatusEnum.PENDING, AnalysisStatusEnum.PROCESSING]:
            task.status = AnalysisStatusEnum.CANCELLED
            await session.commit()
            
            # 这里可以添加取消Celery任务的逻辑
            # 例如：celery_app.control.revoke(task_id, terminate=True)
            
            app_logger.info(f"任务已取消: {task_id}")
            return True
        
        return False
    
    async def retry_task(self, session: AsyncSession, task_id: int) -> AnalysisTask:
        """
        重试失败的任务
        
        Args:
            session: 数据库会话
            task_id: 任务ID
            
        Returns:
            重启的任务对象
        """
        statement = select(AnalysisTask).where(AnalysisTask.id == task_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        
        # 只有失败的任务可以重试
        if task.status != AnalysisStatusEnum.FAILED:
            raise ValueError(f"只有失败的任务可以重试: {task_id}")
        
        # 重置任务状态
        task.status = AnalysisStatusEnum.PENDING
        task.summary = ""
        await session.commit()
        
        # 重新加入队列
        execute_analysis_task.delay(task.id, task.data_id)
        
        app_logger.info(f"任务已重试: {task_id}")
        return task
    
    def load_what_if_model_for_prediction(self, model_name: str, version: int = None):
        """
        加载What-If决策模拟器模型（仅在预测时调用）
        
        Args:
            model_name: 模型名称
            version: 模型版本
            
        Returns:
            加载的模型对象
        """
        return self.task_manager.load_what_if_model_for_prediction(model_name, version)