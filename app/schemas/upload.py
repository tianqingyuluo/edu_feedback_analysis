from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    size: int
    uploaded_at: datetime

class UploadHistory(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total: int
    page: int
    size: int
    items: list[UploadResponse]