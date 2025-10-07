import traceback

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import app_logger
from app.dependencies import get_current_operator, get_db_session
from app.schemas.analysis import AnalysisRequest, AnalysisMetaData
from app.schemas.base_http_response import BaseHTTPResponse
from app.service.analysis_service import AnalysisService
import app.service.analysis_operation_service as operation_service
from app.service.data_clean_service import data_clean_task

router = APIRouter()


@router.get("/", dependencies=[Depends(get_current_operator)])
async def get_all_analysis_tasks(
    db: AsyncSession = Depends(get_db_session),
    analysis_service: AnalysisService = Depends(AnalysisService)
):
    """
    获取所有分析任务的信息
    """
    try:
        tasks = await analysis_service.get_all_analysis_tasks(db)
        return BaseHTTPResponse(
            http_status=200,
            message=tasks
        )
    except Exception as e:
        return BaseHTTPResponse(
            http_status=500,
            message=str(e)
        )


@router.post("/start", dependencies=[Depends(get_current_operator)])
async def start_analysis_task(
    request: AnalysisRequest,
    db: AsyncSession = Depends(get_db_session),
    analysis_service: AnalysisService = Depends(AnalysisService),
    analysis_operation_service: operation_service.AnalysisService = Depends(operation_service.AnalysisService)
):
    """
    启动数据分析任务
    """
    try:
        # 检查数据文件是否存在
        if not await analysis_service.check_data_file_exists(request.dataid, db):
            error_response = BaseHTTPResponse(
                http_status=404,
                message="指定的数据文件不存在"
            )
            return error_response
        
        # 创建分析任务
        task = await analysis_operation_service.create_and_queue_analysis_task(db,request.dataid,)


        task_metadata = AnalysisMetaData(
            taskid=str(task.id),
            dataid=str(task.data_id),
            status=task.status
        )
        return BaseHTTPResponse(
            http_status=202,
            message=task_metadata
        )
    except ValueError as e:
        # 请求参数错误
        error_response = BaseHTTPResponse(
            http_status=400,
            message=str(e)
        )
        return error_response
    except Exception as e:
        # 服务器内部错误
        error_response = BaseHTTPResponse(
            http_status=500,
            message=str(e)
        )
        app_logger.error(traceback.format_exc())
        return error_response


@router.get("/status/{task_id}",dependencies=[Depends(get_current_operator)])
async def get_analysis_status(
    task_id: str,
    db: AsyncSession = Depends(get_db_session),
    analysis_service: AnalysisService = Depends(AnalysisService)
):
    """
    获取指定分析任务的执行状态
    """
    try:
        # 检查任务是否存在
        task_exists = await analysis_service.check_task_exists(task_id, db)
        if not task_exists:
            error_response = BaseHTTPResponse(
                http_status=404,
                message="任务不存在"
            )
            return error_response
        
        # 获取任务状态
        status = await analysis_service.get_analysis_status(task_id, db)
        
        return BaseHTTPResponse(
            http_status=200,
            message=status
        )
    except Exception as e:
        error_response = BaseHTTPResponse(
            http_status=500,
            message=str(e)
        )
        return error_response


@router.get("/results/{task_id}", dependencies=[Depends(get_current_operator)])
async def get_analysis_results(
    task_id: int,
    db: AsyncSession = Depends(get_db_session),
    analysis_service: AnalysisService = Depends(AnalysisService),
    analysis_operation_service: operation_service.AnalysisService = Depends(operation_service.AnalysisService)
):
    """
    获取指定分析任务的结果数据
    """
    try:
        # 检查任务是否存在
        task_exists = await analysis_service.check_task_exists(str(task_id), db)
        if not task_exists:
            error_response = BaseHTTPResponse(
                http_status=404,
                message="任务不存在或结果未生成"
            )
            return error_response
        
        # 检查任务是否已完成
        is_completed = await analysis_service.is_task_completed(str(task_id), db)
        if not is_completed:
            error_response = BaseHTTPResponse(
                http_status=404,
                message="任务尚未完成"
            )
            return error_response
        
        # 获取分析结果
        data_id = await analysis_service.get_data_id_for_task(int(task_id), db)
        df = await data_clean_task(int(task_id), data_id, db)

        results = await analysis_operation_service.generate_comprehensive_analysis(db, int(task_id), df)

        return BaseHTTPResponse(
            http_status=200,
            message=results
        )
    except Exception as e:
        error_response = BaseHTTPResponse(
            http_status=500,
            message=str(e)
        )
        app_logger.error(traceback.format_exc())
        return error_response