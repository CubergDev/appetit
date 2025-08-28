from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sort: int = Field(default=0, ge=0)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    sort: Optional[int] = Field(None, ge=0)


class CategoryOut(BaseModel):
    id: int
    name: str
    sort: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MenuItemCreate(BaseModel):
    category_id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)


class MenuItemUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    image_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class MenuItemOut(BaseModel):
    id: int
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
