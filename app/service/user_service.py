from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.db.models import User
from app.exception.exceptions.user import UserNotFoundError, DuplicateUserError
from app.schemas import UserRead, UserCreate, UserUpdate
from app.core.security import verify_password, get_password_hash
from app.dependencies import get_db_session


class UserService:
    """用户服务"""

    async def get_all_users(self, db: AsyncSession) -> list[UserRead]:
        """获取所有用户"""
        query = select(User)
        result = await db.execute(query)
        users = list(result.scalars().all())
        user_reads = [UserRead.model_validate(user) for user in users]
        return user_reads
    async def create_user(self, user: UserCreate, db: AsyncSession) -> UserRead:
        """创建用户"""
        try:
            user = User.model_validate(user)
            user.password = await get_password_hash(user.password)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return UserRead.model_validate(user)
        except IntegrityError as e:
            await db.rollback()
            raise DuplicateUserError('手机号重复', user.phone)

    async def update_user(self, user_id: int, user: UserUpdate, db: AsyncSession) -> UserRead:
        """更新用户"""
        db_user = await db.get(User, user_id)
        if db_user is None:
            raise UserNotFoundError(user_id)
        try:
            db_user.updated_at = datetime.now(timezone.utc)
            for key, value in user.model_dump().items():
                if key == "password" and value is None:
                    continue
                setattr(db_user, key, value)
            await db.commit()
            await db.refresh(db_user)
            return UserRead.model_validate(db_user)
        except IntegrityError as e:
            await db.rollback()
            raise DuplicateUserError('手机号重复', user.phone)

    async def delete_user(self, user_id: int, db: AsyncSession) -> None:
        """删除用户"""
        db_user = await db.get(User, user_id)
        if db_user is None:
            raise UserNotFoundError(user_id)
        await db.delete(db_user)
        await db.commit()