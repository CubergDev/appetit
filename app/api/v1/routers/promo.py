from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.session import get_db
from app import models
from app.schemas.promo_cart import PromoValidateRequest, PromoValidateResponse
from app.services.promo.validator import calculate_discount

router = APIRouter(prefix="/promo", tags=["promo"])


@router.post("/validate", response_model=PromoValidateResponse)
def validate_promo(payload: PromoValidateRequest, db: Session = Depends(get_db)):
    # Handle subtotal-based validation (for tests)
    if payload.subtotal is not None:
        res = calculate_discount(db, payload.code, Decimal(str(payload.subtotal)))
        response = PromoValidateResponse(valid=res.valid, discount=res.discount, reason=res.reason)
        
        # Add promocode details if valid
        if res.valid and payload.code:
            promo = db.query(models.Promocode).filter(models.Promocode.code == payload.code).first()
            if promo:
                response.promocode = {
                    "code": promo.code,
                    "kind": promo.kind,
                    "value": float(promo.value),
                    "active": promo.active
                }
        return response
    
    # Handle cart-based validation (existing logic)
    if not payload.cart:
        return PromoValidateResponse(valid=True, discount=0.0)

    item_ids = [ci.item_id for ci in payload.cart]
    items = {m.id: m for m in db.query(models.MenuItem).filter(models.MenuItem.id.in_(item_ids)).all()}

    subtotal = 0.0
    for ci in payload.cart:
        mi = items.get(ci.item_id)
        if not mi or not mi.is_active:
            raise HTTPException(status_code=400, detail=f"Invalid item in cart: {ci.item_id}")
        price = float(mi.price)
        if ci.qty <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        subtotal += price * ci.qty

    res = calculate_discount(db, payload.code, Decimal(str(subtotal)))
    return PromoValidateResponse(valid=res.valid, discount=res.discount, reason=res.reason)
