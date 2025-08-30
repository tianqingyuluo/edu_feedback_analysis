from fastapi import APIRouter
from app.api.v1.endpoints.admin import user

router = APIRouter(prefix="/admin", tags=["admin"])

router.include_router(user.router, prefix="/user")