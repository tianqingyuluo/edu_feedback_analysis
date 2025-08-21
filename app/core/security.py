import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

# 密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    :param plain_password: 明文密码
    :param hashed_password: 数据库哈希密码
    :return: bool: 是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    获取密码哈希

    :param password: 明文密码
    :return: str: 密码哈希
    """
    return pwd_context.hash(password)

def create_jwt_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    创建 JWT 令牌

    :param expires_delta: 多长时间过期
    :param data: 数据
    :return: str: JWT 令牌
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def decode_jwt_token(token: str) -> dict:
    """
    解码JWT令牌

    :param token: JWT令牌
    :return: dict: 解码后的数据
    :raise: HTTPException: 令牌无效
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token 已过期")