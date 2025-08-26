from typing import Optional
from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str
    sort: int

    class Config:
        from_attributes = True


class MenuItemOut(BaseModel):
    id: int
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
