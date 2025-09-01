from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_operator, get_db_session
from app.schemas import BaseHTTPResponse
from app.schemas.upload import UploadHistory
from app.service.upload_service import UploadService

router = APIRouter()

@router.get("/{page}/{size}", dependencies=[Depends(get_current_operator)], tags=["history"])
async def get_history(
        page: int,
        size: int,
        db: AsyncSession = Depends(get_db_session),
        upload_service: UploadService = Depends(UploadService)):
    return BaseHTTPResponse(
        http_status=200,
        message=UploadHistory(
            total=await upload_service.get_history_count(db),
            page=page,
            size=size,
            items=await upload_service.get_history_by_page(page, size, db)
        )
    )