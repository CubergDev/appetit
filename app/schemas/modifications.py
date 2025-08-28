from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class ModificationTypeOut(BaseModel):
    id: int
    name: str
    category: str  # 'sauce' or 'removal'
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModificationTypeIn(BaseModel):
    name: str
    category: str  # 'sauce' or 'removal'
    is_default: bool = False
    is_active: bool = True


class OrderItemModificationIn(BaseModel):
    modification_type_id: int
    action: str  # 'add' or 'remove'


class OrderItemModificationOut(BaseModel):
    id: int
    order_item_id: int
    modification_type_id: int
    action: str
    created_at: datetime
    modification_type: Optional[ModificationTypeOut] = None

    class Config:
        from_attributes = True


class BulkModificationRequest(BaseModel):
    order_item_ids: List[int]  # List of order item IDs to modify
    modifications: List[OrderItemModificationIn]


class SingleModificationRequest(BaseModel):
    order_item_id: int
    modifications: List[OrderItemModificationIn]


class ModificationResponse(BaseModel):
    success: bool
    message: str
    modified_items: List[int]  # List of order item IDs that were modified