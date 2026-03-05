from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TemplateColumnResponse(BaseModel):
    id: int
    column_name: str
    column_order: int
    data_type: str = "text"

    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    id: int
    name: str
    original_filename: str
    is_active: bool
    uploaded_by: Optional[int] = None
    created_at: Optional[datetime] = None
    columns: Optional[List[TemplateColumnResponse]] = None

    class Config:
        from_attributes = True


class TemplateUploadResponse(BaseModel):
    template: TemplateResponse
    columns_detected: int
