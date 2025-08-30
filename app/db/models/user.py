from app.db.models.base import BaseModel
from app.enum.enums import UserRole
from sqlmodel import Field

class User(BaseModel, table=True):
    username: str = Field(index=True)
    password: str = Field(nullable=False, min_length=8, max_length=128)
    phone: str = Field(index=True, unique=True, min_length=11, max_length=11)
    role:UserRole = Field(default=UserRole.USER)