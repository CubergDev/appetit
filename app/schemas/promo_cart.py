from typing import List, Optional
from pydantic import BaseModel


class CartItem(BaseModel):
    item_id: int
    qty: int


class PromoValidateRequest(BaseModel):
    code: Optional[str] = None
    cart: List[CartItem]


class PromoValidateResponse(BaseModel):
    valid: bool
    discount: float
    reason: Optional[str] = None


class PriceRequest(BaseModel):
    items: List[CartItem]
    promocode: Optional[str] = None
    fulfillment: str  # delivery|pickup
    address: Optional[str] = None


class PriceDetailsLine(BaseModel):
    item_id: int
    name: str
    qty: int
    unit_price: float
    line_total: float


class PriceResponse(BaseModel):
    subtotal: float
    discount: float
    total: float
    details: List[PriceDetailsLine]
