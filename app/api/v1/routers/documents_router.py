from fastapi import APIRouter

from app.api.v1.endpoints.documents import documents

router = APIRouter(prefix="/documents", tags=["documents"])

router.include_router(documents.router)