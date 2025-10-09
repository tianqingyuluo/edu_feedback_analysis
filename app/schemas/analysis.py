"""
分析任务相关的数据模型
定义API请求和响应的数据结构
"""

from typing import Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.enum.enums import AnalysisStatusEnum


class AnalysisTaskResultResponse(BaseModel):
    """分析任务结果响应"""
    taskid: str = Field(..., description="任务ID")
    dataid: str = Field(..., description="数据ID")
    created_at: datetime = Field(..., description="创建时间")
    summary: str = Field(..., description="任务摘要")
    detailed_results: Dict[str, Any] = Field(..., description="详细结果")

class AnalysisMetaData(BaseModel):
    """分析任务元数据"""
    taskid: str = Field(..., description="任务ID")
    dataid: str = Field(..., description="数据ID")
    status: AnalysisStatusEnum = Field(..., description="任务状态")

class AnalysisTaskStatusResponse(BaseModel):
    """分析任务状态响应"""
    taskid: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float | None = Field(..., description="任务进度")

class AnalysisRequest(BaseModel):
    """分析任务请求"""
    dataid: int = Field(..., description="数据ID")