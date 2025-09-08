from sqlalchemy import DateTime, BIGINT, JSON
from sqlmodel import SQLModel, Field
from snowflake import SnowflakeGenerator
from datetime import datetime, timezone

from app.enum.enums import AnalysisStatusEnum

snowflake = SnowflakeGenerator(42)

class AnalysisTask(SQLModel, table=True):
    """
    分析任务表
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    data_id: int = Field(foreign_key="upload.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    status: AnalysisStatusEnum = Field(default=AnalysisStatusEnum.PENDING, index=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
    summary: str = Field(nullable=True)

class AcademicMaturityProcessorData(SQLModel, table=True):
    """
    学术成熟度数据处理器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))

class CorrelationBasedEHIBuilderData(SQLModel, table=True):
    """
    基于学习关联度的EHI（学习健康指标）构建器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))

class CorrelationBasedRPIBuilderData(SQLModel, table=True):
    """
    基于资源感知度的RPI（资源感知指标）构建器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))

class GroupComparisonRadarChartData(SQLModel, table=True):
    """
    组间比较雷达图构建器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))

class StudentSatisfactionRouteSankeyChartData(SQLModel, table=True):
    """
    学生满意度路径桑基图构建器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))

class StudentTimeAllocationPieChartData(SQLModel, table=True):
    """
    学生时间分配饼图构建器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))

class TeacherStudentInteractionBubbleChartData(SQLModel, table=True):
    """
    教师学生互动气泡图构建器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))

class SatisfactionWholeData(SQLModel, table=True):
    """
    整体满意度分析构建器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))

class SatisfactionPartData(SQLModel, table=True):
    """
    部分满意度分析构建器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))

class StudentPortraitData(SQLModel, table=True):
    """
    学生画像分析构建器的输出
    """
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    task_id: int = Field(foreign_key="analysistask.id", nullable=False, ondelete="CASCADE", index=True, sa_type=BIGINT)
    data: dict = Field(nullable=False, sa_type=JSON)
    comment: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))