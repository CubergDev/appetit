from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app import models
from app.schemas.users import UserMeOut, UserUpdate

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
