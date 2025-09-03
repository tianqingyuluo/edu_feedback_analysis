from sqlalchemy import DateTime, BIGINT
from sqlmodel import SQLModel, Field
from snowflake import SnowflakeGenerator
from datetime import datetime, timezone

snowflake = SnowflakeGenerator(42)

class Upload(SQLModel, table=True):
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    filename: str = Field(nullable=False, unique=True)
    size: int = Field(nullable=False)
    path: str = Field(nullable=False)
    hash: str = Field(nullable=False, unique=True, index=True)
    uploaded_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
