from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.analysis.machine_learing.models import what_if_simulation
from app.analysis.machine_learing.models.what_if_decision_simulator import load_model, send_feature_importance
from app.dependencies import get_db_session
from app.schemas.what_if_decision_simulator import WhatIfInput
from app.service.data_clean_service import data_clean_task

router = APIRouter()

@router.post("/what_if")
async def predict(input_data: WhatIfInput, task_id: str):
    model = await load_model("what_if_decision_simulator", task_id)
    return what_if_simulation(model, input_data)

@router.get("/what_if/{task_id}/{data_id}")
async def get_features(task_id: int, data_id: int, db: AsyncSession = Depends(get_db_session)):
    data = await data_clean_task(task_id, data_id, db)
    return send_feature_importance(data, data["学校整体满意度"], 0.16)