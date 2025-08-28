from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.db.session import get_db
from app import models
from app.schemas.users import UserMeOut, UserUpdate, SavedAddressCreate, SavedAddressUpdate, SavedAddressOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMeOut)
def get_me(user: models.User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=UserMeOut)
def update_me(payload: UserUpdate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # handle email/phone uniqueness if changed
    if payload.email and payload.email != user.email:
        existing = db.query(models.User).filter(models.User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = payload.email
        # when email changes, reset verification flag
        user.is_email_verified = False
    if payload.phone and payload.phone != user.phone:
        existing = db.query(models.User).filter(models.User.phone == payload.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone already in use")
        user.phone = payload.phone
        user.is_phone_verified = False

    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.dob is not None:
        user.dob = payload.dob

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Saved Addresses CRUD endpoints

@router.get("/me/addresses", response_model=List[SavedAddressOut])
def get_my_addresses(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Get all saved addresses for the current user"""
    addresses = db.query(models.SavedAddress).filter(
        models.SavedAddress.user_id == user.id
    ).order_by(models.SavedAddress.is_default.desc(), models.SavedAddress.created_at.desc()).all()
    return addresses


@router.post("/me/addresses", response_model=SavedAddressOut)
def create_address(
    payload: SavedAddressCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Create a new saved address for the current user"""
    # If this is being set as default, unset all other defaults
    if payload.is_default:
        db.query(models.SavedAddress).filter(
            models.SavedAddress.user_id == user.id,
            models.SavedAddress.is_default == True
        ).update({"is_default": False})
    
    # Create new address
    address = models.SavedAddress(
        user_id=user.id,
        address_text=payload.address_text,
        latitude=payload.latitude,
        longitude=payload.longitude,
        label=payload.label,
        is_default=payload.is_default or False
    )
    
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.put("/me/addresses/{address_id}", response_model=SavedAddressOut)
def update_address(
    address_id: int,
    payload: SavedAddressUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Update a saved address for the current user"""
    # Find the address and ensure it belongs to the current user
    address = db.query(models.SavedAddress).filter(
        models.SavedAddress.id == address_id,
        models.SavedAddress.user_id == user.id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # If setting as default, unset all other defaults
    if payload.is_default:
        db.query(models.SavedAddress).filter(
            models.SavedAddress.user_id == user.id,
            models.SavedAddress.id != address_id,
            models.SavedAddress.is_default == True
        ).update({"is_default": False})
    
    # Update fields
    if payload.address_text is not None:
        address.address_text = payload.address_text
    if payload.latitude is not None:
        address.latitude = payload.latitude
    if payload.longitude is not None:
        address.longitude = payload.longitude
    if payload.label is not None:
        address.label = payload.label
    if payload.is_default is not None:
        address.is_default = payload.is_default
    
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.delete("/me/addresses/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Delete a saved address for the current user"""
    # Find the address and ensure it belongs to the current user
    address = db.query(models.SavedAddress).filter(
        models.SavedAddress.id == address_id,
        models.SavedAddress.user_id == user.id
    ).first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    db.delete(address)
    db.commit()
    return {"message": "Address deleted successfully"}


# Admin user management

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    """Delete a user account (Admin only)"""
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has any orders that might need to be preserved
    orders_count = db.query(models.Order).filter(models.Order.user_id == user_id).count()
    if orders_count > 0:
        # Instead of blocking deletion, we could anonymize the user data
        # For now, we'll prevent deletion of users with orders
        raise HTTPException(status_code=400, detail="Cannot delete user with existing orders. Consider deactivating instead.")
    
    # Clean up related data
    # Delete saved addresses
    db.query(models.SavedAddress).filter(models.SavedAddress.user_id == user_id).delete()
    
    # Delete user devices
    db.query(models.Device).filter(models.Device.user_id == user_id).delete()
    
    # Delete verification records
    db.query(models.EmailVerification).filter(models.EmailVerification.user_id == user_id).delete()
    db.query(models.PhoneVerification).filter(models.PhoneVerification.user_id == user_id).delete()
    
    # Delete the user
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}
