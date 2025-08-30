from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings
from app.core.security import create_jwt_token, decode_jwt_token

# 创建HTTP Bearer安全方案实例
security = HTTPBearer()

router = APIRouter()


@router.post("")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    刷新访问令牌接口

    :param credentials: HTTP认证凭证
    :return: 新的访问令牌
    """
    try:
        # 解码当前令牌
        payload = await decode_jwt_token(credentials.credentials)

        # 从令牌中获取用户信息
        user_id = payload.get("user_id")
        phone = payload.get("sub")
        role = payload.get("role")

        if not user_id or not phone or not role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌中缺少必要信息"
            )

        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        new_access_token = await create_jwt_token(
            data={
                "sub": phone,
                "user_id": user_id,
                "role": role
            },
            expires_delta=access_token_expires,
        )

        # 返回新的访问令牌
        return {
            "http_status": 200,
            "access_token": new_access_token,
            "token_type": "Bearer"
        }

    except Exception as e:
        # 重新抛出HTTP异常
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法刷新令牌"
        )