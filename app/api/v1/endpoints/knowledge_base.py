import traceback
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.dependencies import get_current_user, get_db_session, get_knowledge_base_service, get_rag_service
from app.db.models import User, KnowledgeBase
from app.schemas import BaseHTTPResponse, HttpResponseWithData
from app.service.document_service import KnowledgeBaseService
from app.service.rag_service import RAGService
from app.core.logging import app_logger

router = APIRouter()

class CreateKnowledgeBaseRequest(BaseModel):
    name: str
    description: str = ""

class InitializeKnowledgeBaseRequest(BaseModel):
    document_ids: List[int]

@router.post("/", dependencies=[Depends(get_current_user)])
async def create_knowledge_base(
    request: CreateKnowledgeBaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    kb_service: KnowledgeBaseService = Depends(get_knowledge_base_service)
):
    """创建知识库"""
    try:
        kb = await kb_service.create_knowledge_base(
            name=request.name,
            description=request.description,
            db=db
        )
        
        return HttpResponseWithData(
            http_status=201,
            message="知识库创建成功",
            data={
                "id": str(kb.id),
                "name": kb.name,
                "description": kb.description,
                "status": kb.status,
                "embedding_model": kb.embedding_model,
                "llm_model": kb.llm_model,
                "created_at": kb.created_at
            }
        )

    except ValueError as e:
        app_logger.error(f"创建知识库失败: {str(e)}")
        return BaseHTTPResponse(
            http_status=400,
            message=str(e)
        )
    except Exception as e:
        app_logger.error(f"创建知识库异常: {str(e)}")
        return BaseHTTPResponse(
            http_status=500,
            message="创建知识库失败，请稍后重试"
        )

@router.post("/{kb_id}/initialize", dependencies=[Depends(get_current_user)])
async def initialize_knowledge_base(
    kb_id: int,
    request: InitializeKnowledgeBaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    kb_service: KnowledgeBaseService = Depends(KnowledgeBaseService),
    rag_service: RAGService = Depends(get_rag_service)
):
    """初始化知识库：处理文档并创建向量索引"""
    try:
        # 检查知识库是否存在
        kb = await kb_service.get_knowledge_base(kb_id, db)
        basename = kb.name
        if not kb:
            return BaseHTTPResponse(
                http_status=404,
                message="知识库不存在"
            )

        # 更新状态为初始化中
        await kb_service.update_knowledge_base_status(kb_id, "initializing", db=db)

        # 获取文档路径
        from app.db.models.document import Document
        from sqlmodel import select
        
        doc_query = select(Document).where(Document.id.in_(request.document_ids))
        doc_result = await db.execute(doc_query)
        documents = doc_result.scalars().all()
        
        if not documents:
            await kb_service.update_knowledge_base_status(
                kb_id, "error", "没有找到有效的文档", db=db
            )
            return BaseHTTPResponse(
                http_status=400,
                message="没有找到有效的文档"
            )

        # 检查所有文档是否都已处理
        unprocessed_docs = [doc for doc in documents if doc.status != "processed"]
        if unprocessed_docs:
            await kb_service.update_knowledge_base_status(
                kb_id, "error", f"存在未处理的文档: {[doc.filename for doc in unprocessed_docs]}", db=db
            )
            return BaseHTTPResponse(
                http_status=400,
                message=f"存在未处理的文档: {[doc.filename for doc in unprocessed_docs]}"
            )

        # 获取文档路径列表
        file_paths = [doc.file_path for doc in documents]
        
        # 初始化RAG知识库
        rag_service.initialize_knowledge_base(file_paths, kb_id)
        
        # 更新知识库状态和统计信息
        total_chunks = sum(doc.chunk_count for doc in documents)
        await kb_service.update_knowledge_base_status(kb_id, "ready", db=db)
        
        # 更新文档数量和块数量
        from sqlmodel import update
        await db.execute(
            update(KnowledgeBase)
            .where(KnowledgeBase.id == kb_id)
            .values(
                document_count=len(documents),
                total_chunks=total_chunks
            )
        )

        await db.commit()

        app_logger.info(f"知识库初始化成功: {basename}, 文档数: {len(documents)}, 块数: {total_chunks}")
        
        return HttpResponseWithData(
            http_status=200,
            message="知识库初始化成功",
            data={
                "kb_id": str(kb_id),
                "document_count": len(documents),
                "total_chunks": total_chunks,
                "status": "ready"
            }
        )

    except Exception as e:
        await kb_service.update_knowledge_base_status(kb_id, "error", str(e), db=db)
        app_logger.error(f"知识库初始化异常: {str(e)}")
        app_logger.error(traceback.format_exc())
        return BaseHTTPResponse(
            http_status=500,
            message=f"知识库初始化失败: {str(e)}"
        )

@router.post("/{kb_id}/update", dependencies=[Depends(get_current_user)])
async def update_knowledge_base(
    kb_id: int,
    request: InitializeKnowledgeBaseRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    kb_service: KnowledgeBaseService = Depends(KnowledgeBaseService),
    rag_service: RAGService = Depends(get_rag_service)
):
    """更新知识库：添加新文档"""
    try:
        # 检查知识库是否存在
        kb = await kb_service.get_knowledge_base(kb_id, db)
        basename = kb.name
        if not kb:
            return BaseHTTPResponse(
                http_status=404,
                message="知识库不存在"
            )

        # 更新状态为更新中
        await kb_service.update_knowledge_base_status(kb_id, "updating", db=db)

        # 获取新文档
        from app.db.models.document import Document
        from sqlmodel import select
        
        doc_query = select(Document).where(Document.id.in_(request.document_ids))
        doc_result = await db.execute(doc_query)
        new_documents = doc_result.scalars().all()
        
        if not new_documents:
            await kb_service.update_knowledge_base_status(
                kb_id, "error", "没有找到有效的文档", db=db
            )
            return BaseHTTPResponse(
                http_status=400,
                message="没有找到有效的文档"
            )

        # 检查所有文档是否都已处理
        unprocessed_docs = [doc for doc in new_documents if doc.status != "processed"]
        if unprocessed_docs:
            await kb_service.update_knowledge_base_status(
                kb_id, "error", f"存在未处理的文档: {[doc.filename for doc in unprocessed_docs]}", db=db
            )
            return BaseHTTPResponse(
                http_status=400,
                message=f"存在未处理的文档: {[doc.filename for doc in unprocessed_docs]}"
            )

        # 获取文档路径列表
        file_paths = [doc.file_path for doc in new_documents]
        
        # 更新RAG知识库（这会自动处理去重）
        rag_service.initialize_knowledge_base(file_paths)
        
        # 更新知识库状态和统计信息
        await kb_service.update_knowledge_base_status(kb_id, "ready", db=db)
        
        # 更新文档数量和块数量
        from sqlmodel import update, select, func
        # 获取当前知识库中的文档总数
        current_docs_query = select(func.count()).select_from(Document).where(Document.status == "processed")
        current_docs_count = await db.execute(current_docs_query)
        total_docs = current_docs_count.scalar()
        
        # 获取当前总块数
        current_chunks_query = select(func.sum(Document.chunk_count)).select_from(Document).where(Document.status == "processed")
        current_chunks_result = await db.execute(current_chunks_query)
        total_chunks = current_chunks_result.scalar() or 0
        
        await db.execute(
            update(KnowledgeBase)
            .where(KnowledgeBase.id == kb_id)
            .values(
                document_count=total_docs,
                total_chunks=total_chunks
            )
        )
        await db.commit()

        app_logger.info(f"知识库更新成功: {basename}, 新增文档数: {len(new_documents)}")
        
        return HttpResponseWithData(
            http_status=200,
            message="知识库更新成功",
            data={
                "kb_id": str(kb_id),
                "added_documents": len(new_documents),
                "total_documents": total_docs,
                "total_chunks": total_chunks,
                "status": "ready"
            }
        )

    except Exception as e:
        await kb_service.update_knowledge_base_status(kb_id, "error", str(e), db=db)
        app_logger.error(f"知识库更新异常: {str(e)}")
        return BaseHTTPResponse(
            http_status=500,
            message=f"知识库更新失败: {str(e)}"
        )

@router.get("/{kb_id}", dependencies=[Depends(get_current_user)])
async def get_knowledge_base(
    kb_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    kb_service: KnowledgeBaseService = Depends(get_knowledge_base_service)
):
    """获取知识库信息"""
    try:
        kb = await kb_service.get_knowledge_base(kb_id, db)
        if not kb:
            return BaseHTTPResponse(
                http_status=404,
                message="知识库不存在"
            )

        return HttpResponseWithData(
            http_status=200,
            message="获取知识库信息成功",
            data={
                "id": str(kb.id),
                "name": kb.name,
                "description": kb.description,
                "status": kb.status,
                "document_count": kb.document_count,
                "total_chunks": kb.total_chunks,
                "embedding_model": kb.embedding_model,
                "llm_model": kb.llm_model,
                "created_at": kb.created_at,
                "updated_at": kb.updated_at,
                "last_indexed_at": kb.last_indexed_at,
                "error_message": kb.error_message
            }
        )

    except Exception as e:
        app_logger.error(f"获取知识库信息异常: {str(e)}")
        return BaseHTTPResponse(
            http_status=500,
            message="获取知识库信息失败，请稍后重试"
        )

@router.get("/", dependencies=[Depends(get_current_user)])
async def get_knowledge_bases(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    kb_service: KnowledgeBaseService = Depends(get_knowledge_base_service)
):
    """获取所有知识库列表"""
    try:
        kbs = await kb_service.get_knowledge_bases(db)
        
        kb_list = []
        for kb in kbs:
            kb_list.append({
                "id": str(kb.id),
                "name": kb.name,
                "description": kb.description,
                "status": kb.status,
                "document_count": kb.document_count,
                "total_chunks": kb.total_chunks,
                "embedding_model": kb.embedding_model,
                "llm_model": kb.llm_model,
                "created_at": kb.created_at,
                "updated_at": kb.updated_at,
                "last_indexed_at": kb.last_indexed_at
            })

        return HttpResponseWithData(
            http_status=200,
            message="获取知识库列表成功",
            data={"knowledge_bases": kb_list}
        )

    except Exception as e:
        app_logger.error(f"获取知识库列表异常: {str(e)}")
        return BaseHTTPResponse(
            http_status=500,
            message="获取知识库列表失败，请稍后重试"
        )

@router.delete("/{kb_id}", dependencies=[Depends(get_current_user)])
async def delete_knowledge_base(
    kb_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    kb_service: KnowledgeBaseService = Depends(get_knowledge_base_service)
):
    """删除知识库"""
    try:
        success = await kb_service.delete_knowledge_base(kb_id, db)
        if success:
            return BaseHTTPResponse(
                http_status=204,
                message="知识库删除成功"
            )
        else:
            return BaseHTTPResponse(
                http_status=404,
                message="知识库不存在"
            )

    except Exception as e:
        app_logger.error(f"删除知识库异常: {str(e)}")
        return BaseHTTPResponse(
            http_status=500,
            message="删除知识库失败，请稍后重试"
        )

@router.get("/{kb_id}/status", dependencies=[Depends(get_current_user)])
async def check_knowledge_base_status(
    kb_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    kb_service: KnowledgeBaseService = Depends(KnowledgeBaseService)
):
    """检查知识库状态"""
    try:
        kb = await kb_service.get_knowledge_base(kb_id, db)
        if not kb:
            return BaseHTTPResponse(
                http_status=404,
                message="知识库不存在"
            )

        return HttpResponseWithData(
            http_status=200,
            message="获取知识库状态成功",
            data={
                "kb_id": kb_id,
                "status": kb.status,
                "document_count": kb.document_count,
                "total_chunks": kb.total_chunks,
                "last_indexed_at": kb.last_indexed_at,
                "error_message": kb.error_message
            }
        )

    except Exception as e:
        app_logger.error(f"检查知识库状态异常: {str(e)}")
        return BaseHTTPResponse(
            http_status=500,
            message="检查知识库状态失败，请稍后重试"
        )