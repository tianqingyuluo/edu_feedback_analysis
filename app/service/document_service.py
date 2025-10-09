import hashlib
import json
import os.path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, func, update

from app.core.config import settings
from app.core.logging import app_logger
from app.db.models.document import Document, KnowledgeBase
from app.db.models.upload import Upload
from app.rag.processor.data_loader import load_documents
from app.rag.processor.text_spliter import split_documents


class DocumentService:
    """文档管理服务"""

    def __init__(self):
        self.document_storage_path = settings.analysis_file_path + "rag_documents/"

    async def upload_document(self, file: UploadFile, db: AsyncSession) -> Dict[str, Any]:
        """上传文档到RAG系统"""
        filename = file.filename
        file_path = f"{self.document_storage_path}{filename}"
        
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        content: bytes = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        file_type = filename.lower().split('.')[-1] if '.' in filename else 'unknown'

        try:
            # 保存文件
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

            # 创建文档记录
            document = Document(
                filename=filename,
                file_path=file_path,
                file_size=len(content),
                file_hash=file_hash,
                file_type=file_type,
                status="uploaded"
            )
            db.add(document)
            await db.commit()
            await db.refresh(document)

            app_logger.info(f"文档上传成功: {filename}, ID: {document.id}")
            return {
                "id": document.id,
                "filename": document.filename,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "status": document.status,
                "uploaded_at": document.uploaded_at
            }

        except IntegrityError:
            await db.rollback()
            raise ValueError(f"文档 {filename} 已存在")
        except Exception as e:
            await db.rollback()
            # 删除已保存的文件
            if os.path.exists(file_path):
                os.remove(file_path)
            raise ValueError(f"文档上传失败: {str(e)}")

    # async def process_document(self, document_id: int, db: AsyncSession) -> Dict[str, Any]:
    #     """处理文档：分割文本并准备向量化"""
    #     document = await db.get(Document, document_id)
    #     if not document:
    #         raise ValueError(f"文档 {document_id} 不存在")
    #
    #     file_path = document.file_path
    #     filename = document.filename
    #     try:
    #         # 更新状态为处理中
    #         document.status = "processing"
    #         await db.flush()
    #
    #         # 加载文档
    #         documents = load_documents([file_path])
    #         if not documents:
    #             raise ValueError("无法加载文档内容")
    #
    #         # 分割文档
    #         split_docs = split_documents(documents)
    #         chunk_count = len(split_docs)
    #
    #         # # 重新获取文档对象以确保会话状态正确
    #         # document = await db.get(Document, document_id)
    #
    #         # 更新文档信息
    #         document.chunk_count = chunk_count
    #         document.status = "processed"
    #         document.processed_at = datetime.now(timezone.utc)
    #         document.doc_metadata = json.dumps({
    #             "source": documents[0].get("metadata", {}),
    #             "chunk_size": 1000,
    #             "chunk_overlap": 200
    #         })
    #
    #         await db.commit()
    #         app_logger.info(f"文档处理成功: {document.filename}, 分割为 {chunk_count} 个块")
    #
    #         return {
    #             "id": document.id,
    #             "filename": document.filename,
    #             "status": document.status,
    #             "chunk_count": document.chunk_count,
    #             "processed_at": document.processed_at
    #         }
    #
    #     except Exception as e:
    #         await db.rollback()
    #         # 为了清晰和安全，我们重新获取并更新状态
    #         document_for_error = await db.get(Document, document_id)
    #         document_for_error.status = "failed"
    #         document_for_error.error_message = str(e)
    #         await db.commit()
    #         app_logger.error(f"文档处理失败: {filename}, 错误: {str(e)}")
    #         raise ValueError(f"文档处理失败: {str(e)}")

    async def process_document(
        self, document_id: int, db: AsyncSession
    ) -> Dict[str, Any]:
        """处理文档：分割文本并准备向量化"""

        # 使用事务上下文管理器确保原子性
        async with db.begin_nested():
            # 在事务内获取文档对象
            document = await db.get(Document, document_id)
            if not document:
                raise ValueError(f"文档 {document_id} 不存在")

            file_path = document.file_path
            filename = document.filename

            try:
                # 更新状态为处理中
                document.status = "processing"
                await db.flush()  # 使用 flush 而不是 commit

                # 加载文档（同步操作）
                documents = load_documents([file_path])
                if not documents:
                    raise ValueError("无法加载文档内容")

                # 分割文档
                split_docs = split_documents(documents)
                chunk_count = len(split_docs)

                # 更新文档信息
                document.chunk_count = chunk_count
                document.status = "processed"
                document.processed_at = datetime.now(timezone.utc)
                document.doc_metadata = json.dumps(
                    {
                        "source": documents[0].get("metadata", {}),
                        "chunk_size": 1000,
                        "chunk_overlap": 200,
                    }
                )

                app_logger.info(
                    f"文档处理成功: {document.filename}, 分割为 {chunk_count} 个块"
                )
                res = {
                    "id": str(document.id),
                    "filename": document.filename,
                    "status": document.status,
                    "chunk_count": document.chunk_count,
                    "processed_at": document.processed_at,
                }
                
                await db.commit()

                return res

            except Exception as e:
                # 在同一个事务中处理错误
                document.status = "failed"
                document.error_message = str(e)
                app_logger.error(f"文档处理失败: {filename}, 错误: {str(e)}")
                raise ValueError(f"文档处理失败: {str(e)}")

    async def delete_document(self, document_id: int, db: AsyncSession) -> bool:
        """删除文档"""
        try:
            document = await db.get(Document, document_id)
            if not document:
                return False

            # 删除文件
            if os.path.exists(document.file_path):
                os.remove(document.file_path)

            # 删除数据库记录
            await db.delete(document)
            await db.commit()

            app_logger.info(f"文档删除成功: {document.filename}")
            return True

        except Exception as e:
            await db.rollback()
            app_logger.error(f"文档删除失败: {str(e)}")
            return False

    async def get_document(self, document_id: int, db: AsyncSession) -> Optional[Document]:
        """获取单个文档信息"""
        return await db.get(Document, document_id)

    async def get_documents(self, page: int = 1, page_size: int = 20, 
                          status: Optional[str] = None, db: AsyncSession = None) -> Dict[str, Any]:
        """获取文档列表"""
        offset = (page - 1) * page_size
        
        query = select(Document)
        if status:
            query = query.where(Document.status == status)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await db.execute(count_query)
        total = total_count.scalar()
        
        # 获取文档列表
        query = query.offset(offset).limit(page_size).order_by(Document.uploaded_at.desc())
        result = await db.execute(query)
        documents = result.scalars().all()

        return {
            "documents": documents,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def get_document_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """获取文档统计信息"""
        # 总文档数
        total_docs = await db.execute(select(func.count()).select_from(Document))
        total_count = total_docs.scalar()

        # 按状态统计
        status_stats = await db.execute(
            select(Document.status, func.count(Document.id))
            .group_by(Document.status)
        )
        status_counts = dict(status_stats.all())

        # 按类型统计
        type_stats = await db.execute(
            select(Document.file_type, func.count(Document.id))
            .group_by(Document.file_type)
        )
        type_counts = dict(type_stats.all())

        # 总块数
        total_chunks = await db.execute(
            select(func.sum(Document.chunk_count)).select_from(Document)
            .where(Document.status == "processed")
        )
        chunk_count = total_chunks.scalar() or 0

        return {
            "total_documents": total_count,
            "status_distribution": status_counts,
            "type_distribution": type_counts,
            "total_chunks": chunk_count
        }


class KnowledgeBaseService:
    """知识库管理服务"""

    async def create_knowledge_base(self, name: str, description: str = "", db: AsyncSession = None) -> KnowledgeBase:
        """创建知识库"""
        try:
            kb = KnowledgeBase(
                name=name,
                description=description,
                embedding_model=settings.embedding_model_name,
                llm_model=settings.llm_model_name
            )
            db.add(kb)
            await db.commit()
            await db.refresh(kb)
            
            app_logger.info(f"知识库创建成功: {name}")
            return kb

        except IntegrityError:
            await db.rollback()
            raise ValueError(f"知识库名称 {name} 已存在")

    async def get_knowledge_base(self, kb_id: int, db: AsyncSession) -> Optional[KnowledgeBase]:
        """获取知识库信息"""
        return await db.get(KnowledgeBase, kb_id)

    async def get_knowledge_bases(self, db: AsyncSession) -> List[KnowledgeBase]:
        """获取所有知识库"""
        result = await db.execute(select(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()))
        return result.scalars().all()

    async def update_knowledge_base_status(self, kb_id: int, status: str, 
                                         error_message: str = None, db: AsyncSession = None) -> bool:
        """更新知识库状态"""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now(timezone.utc)
            }
            if error_message:
                update_data["error_message"] = error_message
            if status == "ready":
                update_data["last_indexed_at"] = datetime.now(timezone.utc)

            await db.execute(
                update(KnowledgeBase)
                .where(KnowledgeBase.id == kb_id)
                .values(**update_data)
            )
            await db.commit()
            return True

        except Exception as e:
            await db.rollback()
            app_logger.error(f"更新知识库状态失败: {str(e)}")
            return False

    async def delete_knowledge_base(self, kb_id: int, db: AsyncSession) -> bool:
        """删除知识库"""
        try:
            kb = await db.get(KnowledgeBase, kb_id)
            if not kb:
                return False

            await db.delete(kb)
            await db.commit()
            
            app_logger.info(f"知识库删除成功: {kb.name}")
            return True

        except Exception as e:
            await db.rollback()
            app_logger.error(f"知识库删除失败: {str(e)}")
            return False