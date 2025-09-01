from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.enum.enums import UserRole


class UserRead(BaseModel):
    """用户模型"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str
    phone: str
    role: UserRole
    created_at: datetime
    updated_at: datetime

class UserCreate(BaseModel):
    """用户创建模型"""
    model_config = ConfigDict(from_attributes=True)
    username: str
    phone: str
    password: str

class UserUpdate(BaseModel):
    """用户更新模型"""
    model_config = ConfigDict(from_attributes=True)
    username: str
    password: str
    phone: str
    role: UserRole

class UserLogin(BaseModel):
    """用户登录模型"""
    model_config = ConfigDict(from_attributes=True)
    phone: str
    password: str