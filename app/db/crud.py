from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Generic, TypeVar, Optional, Sequence

# 定义类型变量
ModelType = TypeVar("ModelType", bound=SQLModel)

class CRUDBase(Generic[ModelType]):
    """基础CRUD操作类"""
    
    def __init__(self, model: type[ModelType]) -> None:
        """
        初始化CRUD对象
        
        :param model: SQLModel模型类
        """
        self.model = model
    
    async def get(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        """
        根据ID获取单个对象
        
        :param session: 数据库会话
        :param id: 对象ID
        :return: 模型对象或None
        """
        statement = select(self.model).where(self.model.id == id)
        result = await session.exec(statement)
        return result.first_or_none()
    
    async def get_multi(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        """
        获取多个对象（分页）
        
        :param session: 数据库会话
        :param skip: 跳过的记录数
        :param limit: 返回的记录数
        :return: 模型对象列表
        """
        statement = select(self.model).offset(skip).limit(limit)
        result = await session.exec(statement)
        return result.all()
    
    async def create(self, session: AsyncSession, obj_in: ModelType) -> ModelType:
        """
        创建对象
        
        :param session: 数据库会话
        :param obj_in: 要创建的对象
        :return: 创建后的对象
        """
        session.add(obj_in)
        await session.commit()
        await session.refresh(obj_in)
        return obj_in
    
    async def update(
        self, session: AsyncSession, db_obj: ModelType, obj_in: ModelType
    ) -> ModelType:
        """
        更新对象
        
        :param session: 数据库会话
        :param db_obj: 数据库中的对象
        :param obj_in: 包含更新数据的对象
        :return: 更新后的对象
        """
        # 更新对象属性
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
    
    async def remove(self, session: AsyncSession, id: int) -> bool:
        """
        删除对象
        
        :param session: 数据库会话
        :param id: 对象ID
        :return: 是否成功删除
        """
        obj = await self.get(session, id)
        if obj:
            await session.delete(obj)
            await session.commit()
            return True
        return False