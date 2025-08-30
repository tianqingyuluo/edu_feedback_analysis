from typing import Any
from pydantic import BaseModel, ConfigDict
from app.enum.enums import UserRole

class BaseHTTPResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    http_status: int
    message: str | dict[str, Any] | object = ""