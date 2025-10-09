from fastapi import APIRouter
from app.api.v1.routers import (
    auth_router,
    admin_router,
    upload_router,
    analysis_router,
    chat_router,
    predict_router,
    documents_router,
    knowledge_base_router,
)

api_router = APIRouter()

api_router.include_router(auth_router.router)
api_router.include_router(admin_router.router)
api_router.include_router(upload_router.router)
api_router.include_router(analysis_router.router)
api_router.include_router(chat_router.router)
api_router.include_router(predict_router.router)
api_router.include_router(documents_router.router)
api_router.include_router(knowledge_base_router.router)