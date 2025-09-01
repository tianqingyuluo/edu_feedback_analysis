from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.config import settings
from app.core.security import verify_password, create_jwt_token
from app.dependencies import get_db_session
from app.db.models.user import User
from app.schemas.user import UserLogin, UserRead
from app.exception.exceptions.user import InvalidCredentialsError

router = APIRouter()

@router.post("")
async def login(
        credentials: UserLogin,
        db: AsyncSession = Depends(get_db_session)):
    """
    用户登录接口
    
    :param credentials: 登录凭据(手机号和密码)
    :param db: 数据库会话
    :return: 访问令牌和用户信息
    """
    # 根据手机号查找用户
    statement = select(User).where(User.phone == credentials.phone)
    result = await db.execute(statement)
    user = result.scalar_one_or_none()

    # 检查用户是否存在
    if not user:
        raise InvalidCredentialsError()

    # 验证密码
    if not await verify_password(credentials.password, user.password):
        raise InvalidCredentialsError()

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = await create_jwt_token(
        data={"sub": user.phone, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires,
    )
    
    # 返回用户信息和访问令牌
    return {
        "http_status": 200,
        "token": access_token,
        "message": UserRead(
            id=str(user.id),
            username=user.username,
            phone=user.phone,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    }