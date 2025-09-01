from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_operator, get_db_session
from app.schemas import BaseHTTPResponse, UploadResponse
from app.service.upload_service import UploadService

router = APIRouter()

@router.post("/", dependencies=[Depends(get_current_operator)])
async def upload(
        file: Annotated[UploadFile, File()],
        db: AsyncSession = Depends(get_db_session),
        upload_service: UploadService = Depends(UploadService)
):
    response = await upload_service.upload(
        file=file,
        db=db
    )
    return BaseHTTPResponse(
        http_status=201,
        message=response
    )

@router.delete("/{id}", dependencies=[Depends(get_current_operator)])
async def delete(
        id: int,
        db: AsyncSession = Depends(get_db_session),
        upload_service: UploadService = Depends(UploadService)
):
    if await upload_service.delete(id, db):
        return BaseHTTPResponse(
            http_status=204,
            message="删除成功"
        )
    return BaseHTTPResponse(
        http_status=404,
        message="文件不存在"
    )