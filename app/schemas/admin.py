from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class StatusUpdateRequest(BaseModel):
    status: str  # NEW|COOKING|ON_WAY|DELIVERED|CANCELLED


class PromoGenerateRequest(BaseModel):
    prefix: str
    length: int = 6
    count: int = 10
    kind: str = "percent"  # percent|amount
    value: float = 10.0
    active: bool = True
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    max_redemptions: Optional[int] = None
    per_user_limit: Optional[int] = None
    min_subtotal: Optional[float] = None


class PromoGenerateResponse(BaseModel):
    batch_id: int
    generated: int
    prefix: str
    length: int


class AdminPushRequest(BaseModel):
    title: str
    body: str
    audience: str = "all"  # currently supports only "all"


class AdminPushResponse(BaseModel):
    sent: int
