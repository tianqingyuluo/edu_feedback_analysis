from app.api.v1.endpoints.upload import history, upload

from fastapi import APIRouter

router = APIRouter(prefix='/upload', tags=['upload'])

router.include_router(history.router, prefix='/history')
router.include_router(upload.router, prefix='')

