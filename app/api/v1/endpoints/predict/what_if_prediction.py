from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.machine_learing.models import what_if_simulation
from app.analysis.machine_learing.models.what_if_decision_simulator import load_model, send_feature_importance
from app.dependencies import get_db_session
from app.schemas import BaseHTTPResponse
from app.schemas.what_if_decision_simulator import WhatIfInput
from app.service.data_clean_service import data_clean_task

router = APIRouter()

@router.post("/what_if")
async def predict(input_data: WhatIfInput):
    model = await load_model("what_if_decision_simulator", input_data.task_id)
    return BaseHTTPResponse(
        http_status=200,
        message=what_if_simulation(model, input_data)
    )

@router.get("/what_if/{data_id}/{task_id}")
async def get_features(task_id: int, data_id: int, db: AsyncSession = Depends(get_db_session)):
    data = await data_clean_task(task_id, data_id, db)
    model = await load_model("what_if_decision_simulator", str(task_id))
    return BaseHTTPResponse(
        http_status=200,
        message=send_feature_importance(data, data["学校整体满意度"], 0.16, model)
    )