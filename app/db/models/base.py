from sqlalchemy import BIGINT, DateTime
from sqlmodel import SQLModel, Field
from snowflake import SnowflakeGenerator
from datetime import datetime, timezone

# 雪花id生成器
snowflake = SnowflakeGenerator(42)

# 基础模型，设定id和创建更新时间
class BaseModel(SQLModel):
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    created_at: datetime | None = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
    updated_at: datetime | None = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
