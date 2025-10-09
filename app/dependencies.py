from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from collections.abc import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.db.session import get_session
from app.core.security import decode_jwt_token
from app.db.models.user import User
from app.enum.enums import UserRole
from app.exception.exceptions.user import UserNotFoundError, AuthenticationError, AuthorizationError
from app.service.document_service import DocumentService, KnowledgeBaseService
from app.service.rag_service import RAGService

# 创建HTTP Bearer安全方案实例
security = HTTPBearer()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖函数"""
    async with get_session() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    获取当前用户信息的依赖函数
    
    :param credentials: HTTP认证凭证
    :param db: 数据库会话
    :return: 当前用户对象
    :raises: AuthenticationError: 令牌无效或用户不存在
    """
    try:
        # 解码JWT令牌
        payload = await decode_jwt_token(credentials.credentials)
        
        # 从令牌中获取用户ID
        user_id = payload.get("user_id")
        if not user_id:
            raise AuthenticationError("令牌中缺少用户ID")
        
        # 从数据库中获取用户信息
        statement = select(User).where(User.id == user_id)
        result = await db.execute(statement)
        user = result.scalar_one_or_none()
        
        # 检查用户是否存在
        if not user:
            raise UserNotFoundError(user_id)
            
        return user
    except Exception:
        # 重新抛出认证错误，其他异常将由全局异常处理器处理
        raise AuthenticationError("无法验证令牌")

async def get_current_operator(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前操作员用户信息的依赖函数

    :param current_user: 当前用户对象
    :return: 当前操作员用户对象
    :raises: AuthorizationError: 用户不是操作员
    """
    if current_user.role.value != UserRole.OPERATOR.value and current_user.role.value != UserRole.ADMIN.value:
        raise AuthorizationError("需要操作员或者管理员权限")
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前管理员用户信息的依赖函数
    
    :param current_user: 当前用户对象
    :return: 当前管理员用户对象
    :raises: AuthorizationError: 用户不是管理员
    """
    if current_user.role.value != UserRole.ADMIN.value:
        raise AuthorizationError("需要管理员权限")
    return current_user

# 服务依赖注入
def get_document_service() -> DocumentService:
    """获取文档服务实例"""
    return DocumentService()

def get_knowledge_base_service() -> KnowledgeBaseService:
    """获取知识库服务实例"""
    return KnowledgeBaseService()

# 全局RAG服务实例
_rag_service_instance = None

def get_rag_service() -> RAGService:
    """获取RAG服务实例（单例）"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
        # 在这里可以加载已存在的知识库
    return _rag_service_instance
