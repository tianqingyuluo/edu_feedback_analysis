from fastapi import APIRouter

from app.api.v1.endpoints import knowledge_base

router = APIRouter(prefix="/knowledge-base", tags=["knowledge-base"])

router.include_router(knowledge_base.router)