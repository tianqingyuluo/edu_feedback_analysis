import traceback
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db_session, get_document_service
from app.db.models import User
from app.schemas import HttpResponseWithData
from app.service.document_service import DocumentService
from app.core.logging import app_logger

router = APIRouter()

@router.post("../upload", dependencies=[Depends(get_current_user)])
async def upload_document(
    file: Annotated[UploadFile, File()],
    db: AsyncSession = Depends(get_db_session),
    document_service: DocumentService = Depends(get_document_service)
):
    """上传文档到RAG系统"""
    try:
        # 检查文件类型
        allowed_types = ['pdf', 'txt', 'csv', 'docx', 'doc']
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        if file_extension not in allowed_types:
            return HttpResponseWithData(
                http_status=400,
                message=f"不支持的文件类型: {file_extension}。支持的类型: {', '.join(allowed_types)}"
            )

        # 检查文件大小 (50MB限制)
        if file.size and file.size > 50 * 1024 * 1024:
            return HttpResponseWithData(
                http_status=400,
                message="文件大小不能超过50MB"
            )

        result = await document_service.upload_document(file, db)
        result["id"] = str(result.get("id"))
        return HttpResponseWithData(
            http_status=201,
            message="文档上传成功",
            data=result
        )

    except ValueError as e:
        app_logger.error(f"文档上传失败: {str(e)}")
        app_logger.error(traceback.format_exc())
        return HttpResponseWithData(
            http_status=400,
            message=str(e)
        )
    except Exception as e:
        app_logger.error(f"文档上传异常: {str(e)}")
        app_logger.error(traceback.format_exc())
        return HttpResponseWithData(
            http_status=500,
            message="文档上传失败，请稍后重试"
        )

@router.post("/{document_id}/process", dependencies=[Depends(get_current_user)])
async def process_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    document_service: DocumentService = Depends(get_document_service)
):
    """处理文档：分割文本并准备向量化"""
    try:
        result = await document_service.process_document(document_id, db)
        result["id"] = str(result.get("id"))
        return HttpResponseWithData(
            http_status=200,
            message="文档处理成功",
            data=result
        )

    except ValueError as e:
        app_logger.error(f"文档处理失败: {str(e)}")
        return HttpResponseWithData(
            http_status=400,
            message=str(e)
        )
    except Exception as e:
        app_logger.error(f"文档处理异常: {str(e)}")
        app_logger.error(traceback.format_exc())
        return HttpResponseWithData(
            http_status=500,
            message="文档处理失败，请稍后重试"
        )

@router.delete("/{document_id}", dependencies=[Depends(get_current_user)])
async def delete_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    document_service: DocumentService = Depends(get_document_service)
):
    """删除文档"""
    try:
        success = await document_service.delete_document(document_id, db)
        if success:
            return HttpResponseWithData(
                http_status=204,
                message="文档删除成功"
            )
        else:
            return HttpResponseWithData(
                http_status=404,
                message="文档不存在"
            )

    except Exception as e:
        app_logger.error(f"文档删除异常: {str(e)}")
        return HttpResponseWithData(
            http_status=500,
            message="文档删除失败，请稍后重试"
        )

@router.get("/{document_id}", dependencies=[Depends(get_current_user)])
async def get_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    document_service: DocumentService = Depends(get_document_service)
):
    """获取单个文档信息"""
    try:
        document = await document_service.get_document(document_id, db)
        if not document:
            return HttpResponseWithData(
                http_status=404,
                message="文档不存在"
            )

        return HttpResponseWithData(
            http_status=200,
            message="获取文档信息成功",
            data={
                "id": document.id,
                "filename": document.filename,
                "file_type": document.file_type,
                "file_size": document.file_size,
                "status": document.status,
                "chunk_count": document.chunk_count,
                "uploaded_at": document.uploaded_at,
                "processed_at": document.processed_at,
                "error_message": document.error_message
            }
        )

    except Exception as e:
        app_logger.error(f"获取文档信息异常: {str(e)}")
        return HttpResponseWithData(
            http_status=500,
            message="获取文档信息失败，请稍后重试"
        )

@router.get("/", dependencies=[Depends(get_current_user)])
async def get_documents(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="文档状态过滤"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    document_service: DocumentService = Depends(get_document_service)
):
    """获取文档列表"""
    try:
        result = await document_service.get_documents(page, page_size, status, db)
        
        documents_data = []
        for doc in result["documents"]:
            documents_data.append({
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "status": doc.status,
                "chunk_count": doc.chunk_count,
                "uploaded_at": doc.uploaded_at,
                "processed_at": doc.processed_at,
                "error_message": doc.error_message
            })

        return HttpResponseWithData(
            http_status=200,
            message="获取文档列表成功",
            data={
                "documents": documents_data,
                "pagination": {
                    "total": result["total"],
                    "page": result["page"],
                    "page_size": result["page_size"],
                    "total_pages": result["total_pages"]
                }
            }
        )

    except Exception as e:
        app_logger.error(f"获取文档列表异常: {str(e)}")
        return HttpResponseWithData(
            http_status=500,
            message="获取文档列表失败，请稍后重试"
        )

@router.get("/stats", dependencies=[Depends(get_current_user)])
async def get_document_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    document_service: DocumentService = Depends(get_document_service)
):
    """获取文档统计信息"""
    try:
        stats = await document_service.get_document_stats(db)
        return HttpResponseWithData(
            http_status=200,
            message="获取文档统计成功",
            data=stats
        )

    except Exception as e:
        app_logger.error(f"获取文档统计异常: {str(e)}")
        return HttpResponseWithData(
            http_status=500,
            message="获取文档统计失败，请稍后重试"
        )