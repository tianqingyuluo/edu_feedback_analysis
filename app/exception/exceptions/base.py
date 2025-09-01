from typing import Any


class AppException(Exception):
    """应用异常基类"""
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(message)
