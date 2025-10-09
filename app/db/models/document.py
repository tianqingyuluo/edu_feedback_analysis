from sqlalchemy import DateTime, BIGINT, Text
from sqlmodel import SQLModel, Field
from snowflake import SnowflakeGenerator
from datetime import datetime, timezone
from typing import Optional

snowflake = SnowflakeGenerator(42)

class Document(SQLModel, table=True):
    """RAG系统文档模型"""
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    filename: str = Field(nullable=False)
    file_path: str = Field(nullable=False)
    file_size: int = Field(nullable=False)
    file_hash: str = Field(nullable=False, index=True)
    file_type: str = Field(nullable=False)  # pdf, txt, csv, docx等
    status: str = Field(default="uploaded")  # uploaded, processing, processed, failed
    chunk_count: int = Field(default=0)  # 分割后的文档块数量
    uploaded_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
    processed_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))
    error_message: Optional[str] = Field(default=None, sa_type=Text)
    doc_metadata: Optional[str] = Field(default=None, sa_type=Text)  # JSON格式的元数据

class KnowledgeBase(SQLModel, table=True):
    """知识库模型"""
    id: int = Field(default_factory=lambda:next(snowflake), primary_key=True, sa_type=BIGINT)
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = Field(default=None, sa_type=Text)
    status: str = Field(default="initializing")  # initializing, ready, updating, error
    document_count: int = Field(default=0)
    total_chunks: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
    updated_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc), sa_type=DateTime(timezone=True))
    last_indexed_at: Optional[datetime] = Field(default=None, sa_type=DateTime(timezone=True))
    embedding_model: str = Field(nullable=False)
    llm_model: str = Field(nullable=False)
    error_message: Optional[str] = Field(default=None, sa_type=Text)