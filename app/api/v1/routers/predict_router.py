from fastapi import APIRouter

from app.api.v1.endpoints.predict import what_if_prediction

router = APIRouter(prefix="/predict", tags=["predict"])

router.include_router(what_if_prediction.router)