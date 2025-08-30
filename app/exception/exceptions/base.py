from typing import Any


class AppException(Exception):
    """应用异常基类"""
    def __init__(self, message: str, error_code: str, details: dict[str, Any] | None = None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(message)
