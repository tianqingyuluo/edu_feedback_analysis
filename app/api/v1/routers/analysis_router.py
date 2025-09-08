from fastapi import APIRouter
from app.api.v1.endpoints.analysis import analysis

router = APIRouter(prefix='/analysis', tags=['analysis'])

router.include_router(analysis.router, prefix='')