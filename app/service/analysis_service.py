from typing import List

from nbclient.client import timestamp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from win32timezone import utcnow

from app.db.models import Upload
from app.enum.enums import AnalysisStatusEnum
from app.db.models.analysis import AnalysisTask
from app.schemas.analysis import (
    AnalysisMetaData,
    AnalysisTaskStatusResponse,
    AnalysisTaskResultResponse,
)


class AnalysisService:
    """数据分析服务类"""

    async def get_all_analysis_tasks(self, db: AsyncSession) -> List[AnalysisMetaData]:
        """
        获取所有分析任务的信息
        """
        # 这里应该从数据库查询所有分析任务
        # 示例实现，实际需要根据数据库结构进行调整
        statement = select(AnalysisTask)
        result = await db.execute(statement)
        tasks = list(result.scalars().all())

        tasks = [AnalysisMetaData(
            taskid=str(task.id),
            dataid=str(task.data_id),
            status=task.status
        ) for task in tasks]
        return tasks

    async def check_data_file_exists(self, data_id: int, db: AsyncSession) -> bool:
        """
        检查数据文件是否存在
        """
        statement = select(Upload).where(Upload.id == data_id)
        result = await db.execute(statement)
        upload = result.scalar_one_or_none()
        return upload is not None

    async def create_analysis_task(self, data_id: int, db: AsyncSession) -> AnalysisTask:
        """
        创建分析任务
        """
        task = AnalysisTask(
            data_id=data_id,
            status=AnalysisStatusEnum.PENDING,
            summary=""
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def check_task_exists(self, task_id: str, db: AsyncSession) -> bool:
        """
        检查任务是否存在
        """
        task = await db.get(AnalysisTask, int(task_id))
        if task is None:
            return False
        return True

    async def get_analysis_status(self, task_id: str, db: AsyncSession) -> AnalysisTaskStatusResponse:
        """
        获取分析任务状态
        """
        task = await db.get(AnalysisTask, int(task_id))
        if task.status == AnalysisStatusEnum.COMPLETED:
            status = AnalysisTaskStatusResponse(
                taskid=task_id,
                status=AnalysisStatusEnum.COMPLETED,
                progress=100,
            )
            return status
        elif task.status == AnalysisStatusEnum.FAILED:
            status = AnalysisTaskStatusResponse(
                taskid=task_id,
                status=AnalysisStatusEnum.FAILED,
                progress=0,
            )
            return status
        elif task.status == AnalysisStatusEnum.PENDING:
            status = AnalysisTaskStatusResponse(
                taskid=task_id,
                status=AnalysisStatusEnum.PENDING,
                progress=0,
            )
            return status
        else:
            # progress = await get_progress()
            status = AnalysisTaskStatusResponse(
                taskid=task_id,
                status=AnalysisStatusEnum.PROCESSING,
                progress=1 #progress,
            )
            return status


    async def is_task_completed(self, task_id: str, db: AsyncSession) -> bool:
        """
        检查任务是否已完成
        """
        task = await db.get(AnalysisTask, int(task_id))
        if task.status == AnalysisStatusEnum.COMPLETED:
            return True
        return False

    async def get_analysis_results(self, task_id: str, db: AsyncSession) -> AnalysisTaskResultResponse:
        """
        获取分析结果
        """
        # 这里应该从数据库查询分析结果
        # 示例实现，实际需要根据数据库结构进行调整
        from datetime import datetime
        task = await db.get(AnalysisTask, int(task_id))
        result = AnalysisTaskResultResponse(
            task_id=task_id,
            data_id=str(task.data_id),
            created_at=datetime.now(),
            summary=task.summary,
            detailed_results={"charts": [], "statistics": {}}
        )
        return result

    async def get_data_id_for_task(self, task_id, db):
        task = await db.get(AnalysisTask, task_id)
        return task.data_id