from typing import Optional
from pydantic import BaseModel, EmailStr


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

    class Config:
        from_attributes = True
