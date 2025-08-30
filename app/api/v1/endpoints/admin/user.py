from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UserCreate, UserRead, BaseHTTPResponse, UserUpdate
from app.service import UserService
from app.dependencies import get_current_admin_user, get_db_session

router = APIRouter()

@router.get("", dependencies=[Depends(get_current_admin_user)])
async def get_users(user_service: UserService = Depends(UserService), db: AsyncSession = Depends(get_db_session)):
    users: list[UserRead] = await user_service.get_all_users(db)
    return BaseHTTPResponse(
        http_status=200,
        message={
            "users": users
        }
    )

@router.post("", dependencies=[Depends(get_current_admin_user)])
async def create_user(
        user_create: UserCreate,
        user_service: UserService = Depends(UserService),
        db: AsyncSession = Depends(get_db_session)):
    user: UserRead = await user_service.create_user(user_create, db)
    return BaseHTTPResponse(
        http_status=201,
        message=user
    )

@router.put("/{id}", dependencies=[Depends(get_current_admin_user)])
async def update_user(id: int,
                      user_update: UserUpdate,
                      user_service: UserService = Depends(UserService),
                      db: AsyncSession = Depends(get_db_session)):
    user: UserRead = await user_service.update_user(id, user_update, db)
    return BaseHTTPResponse(
        http_status=200,
        message=user
    )

@router.delete("/{id}", dependencies=[Depends(get_current_admin_user)])
async def delete_user(id: int, user_service: UserService = Depends(UserService), db: AsyncSession = Depends(get_db_session)):
    await user_service.delete_user(id, db)
    return BaseHTTPResponse(
        http_status=204,
        message="删除成功"
    )