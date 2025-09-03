from .base import AppException

class UploadException(AppException):
    pass

class FileConflictError(UploadException):
    def __init__(self, filename: str):
        super().__init__(
            message=f"文件 {filename} 已存在",
            error_code="FILE_CONFLICT"
        )