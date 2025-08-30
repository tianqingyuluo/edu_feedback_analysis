from .base import AppException

class UserException(AppException):
    """用户相关异常基类"""
    pass

class UserNotFoundError(UserException):
    """用户不存在"""
    def __init__(self, user_id: int):
        super().__init__(
            message=f"用户 {user_id} 无法找到",
            error_code="USER_NOT_FOUND",
        )

class DuplicateUserError(UserException):
    """创建用户时用户已存在"""
    def __init__(self, field: str, value: str):
        super().__init__(
            message=f"用户 {field} '{value}' 已经存在",
            error_code="DUPLICATE_USER",
        )

class InvalidCredentialsError(UserException):
    def __init__(self):
        super().__init__(
            message="无效的用户名或密码",
            error_code="INVALID_CREDENTIALS"
        )

class AuthenticationError(UserException):
    """认证错误"""
    def __init__(self, detail: str = "无法验证凭据"):
        super().__init__(
            message=detail,
            error_code="AUTHENTICATION_ERROR"
        )

class AuthorizationError(UserException):
    """授权错误"""
    def __init__(self, detail: str = "权限不足"):
        super().__init__(
            message=detail,
            error_code="AUTHORIZATION_ERROR"
        )