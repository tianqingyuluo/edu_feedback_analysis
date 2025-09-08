from fastapi import APIRouter
from app.api.v1.routers import auth_router, admin_router, upload_router, analysis_router

api_router = APIRouter()

api_router.include_router(auth_router.router)
api_router.include_router(admin_router.router)
api_router.include_router(upload_router.router)
api_router.include_router(analysis_router.router)