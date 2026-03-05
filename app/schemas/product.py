from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class ProductCreate(BaseModel):
    values: Dict[str, str] = {}
    category_id: Optional[int] = None


class ProductUpdate(BaseModel):
    values: Optional[Dict[str, str]] = None
    category_id: Optional[int] = None
    status: Optional[str] = None


class ProductValueResponse(BaseModel):
    column_id: int
    column_name: str
    value: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    template_id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    status: str
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    values: List[ProductValueResponse] = []


class ProductListResponse(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    per_page: int


class BulkImportResponse(BaseModel):
    imported: int
    errors: List[str] = []
