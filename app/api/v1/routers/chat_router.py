from fastapi import APIRouter
from app.api.v1.endpoints.chat import history, send, chatroom

router = APIRouter(prefix="/chat", tags=["chat"])

router.include_router(history.router)
router.include_router(send.router)
router.include_router(chatroom.router)



