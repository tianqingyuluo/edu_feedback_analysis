from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.lifespan import lifespan
from app.api.v1.routers import api_router
from app.exception.exception_handlers import (
    app_exception_handler,
    user_not_found_handler,
    invalid_credentials_handler,
    authentication_error_handler,
    authorization_error_handler,
    validation_exception_handler
)
from app.exception.exceptions.base import AppException
from app.exception.exceptions.user import UserNotFoundError, InvalidCredentialsError, AuthenticationError, AuthorizationError
from fastapi.exceptions import RequestValidationError

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    lifespan=lifespan
)

# 注册全局异常处理器
app.add_exception_handler(AppException, app_exception_handler) # type: ignore
app.add_exception_handler(UserNotFoundError, user_not_found_handler) # type: ignore
app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler) # type: ignore
app.add_exception_handler(AuthenticationError, authentication_error_handler) # type: ignore
app.add_exception_handler(AuthorizationError, authorization_error_handler) # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler) # type: ignore

# 允许所有跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router.api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}