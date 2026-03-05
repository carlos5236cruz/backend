from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryAttributeCreate(BaseModel):
    attribute_name: str
    default_value: Optional[str] = None


class CategoryAttributeResponse(BaseModel):
    id: int
    attribute_name: str
    default_value: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    attributes: Optional[List[CategoryAttributeCreate]] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    created_at: Optional[datetime] = None
    attributes: List[CategoryAttributeResponse] = []

    class Config:
        from_attributes = True
