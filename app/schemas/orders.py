from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from .modifications import OrderItemModificationIn, OrderItemModificationOut


class OrderItemIn(BaseModel):
    item_id: int
    qty: int
    modifications: Optional[List[OrderItemModificationIn]] = []


class OrderCreateRequest(BaseModel):
    items: List[OrderItemIn]
    fulfillment: str  # delivery|pickup
    address_text: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    promocode: Optional[str] = None
    payment_method: Optional[str] = "cod"  # cod|online
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    ga_client_id: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    fulfillment: Optional[str] = None  # delivery|pickup
    address_text: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    paid: Optional[bool] = None
    payment_method: Optional[str] = None


class OrderItemOut(BaseModel):
    id: int
    item_id: Optional[int]
    name_snapshot: str
    qty: int
    price_at_moment: float
    modifications: Optional[List[OrderItemModificationOut]] = []

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    number: str
    status: str
    fulfillment: str
    address_text: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    subtotal: float
    discount: float
    total: float
    paid: bool
    payment_method: str
    promocode_code: Optional[str] = None
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: List[OrderOut]


class CommentIn(BaseModel):
    text: str


class CommentOut(BaseModel):
    id: int
    author_user_id: Optional[int]
    author_role: str
    text: str
    created_at: datetime

    class Config:
        from_attributes = True
