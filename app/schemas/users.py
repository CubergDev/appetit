from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr


class SavedAddressCreate(BaseModel):
    address_text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    label: Optional[str] = None
    is_default: Optional[bool] = False


class SavedAddressUpdate(BaseModel):
    address_text: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    label: Optional[str] = None
    is_default: Optional[bool] = None


class SavedAddressOut(BaseModel):
    id: int
    address_text: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    label: Optional[str] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    dob: Optional[str] = None


class UserMeOut(BaseModel):
    id: int
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: str
    is_email_verified: bool
    is_phone_verified: bool
    saved_addresses: List[SavedAddressOut] = []

    class Config:
        from_attributes = True
