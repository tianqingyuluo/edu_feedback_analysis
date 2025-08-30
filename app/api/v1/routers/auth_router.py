from fastapi import APIRouter
from app.api.v1.endpoints.auth import login, refresh_token, me

router = APIRouter(prefix='/auth', tags=['auth'])

router.include_router(login.router, prefix='/login')
router.include_router(refresh_token.router, prefix='/refresh')
router.include_router(me.router, prefix='/me')