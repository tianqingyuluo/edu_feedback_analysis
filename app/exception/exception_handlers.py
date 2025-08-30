from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.exception.exceptions.base import AppException
from app.exception.exceptions.user import UserNotFoundError, InvalidCredentialsError, AuthenticationError, AuthorizationError


async def app_exception_handler(request: Request, exc: AppException):
    """应用异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "http_status": 400,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    """用户未找到异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "http_status": 404,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    """无效凭证异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "http_status": 401,
            "error_code": exc.error_code,
            "message": exc.message
        }
    )


async def authentication_error_handler(request: Request, exc: AuthenticationError):
    """认证错误异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "http_status": 401,
            "error_code": exc.error_code,
            "message": exc.message
        }
    )


async def authorization_error_handler(request: Request, exc: AuthorizationError):
    """授权错误异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "http_status": 403,
            "error_code": exc.error_code,
            "message": exc.message
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """验证异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "http_status": 422,
            "error_code": "VALIDATION_ERROR",
            "message": "Validation error",
            "details": exc.errors()
        }
    )