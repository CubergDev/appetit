from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import models
from app.schemas.promo_cart import PromoValidateRequest, PromoValidateResponse
from app.services.promo.validator import calculate_discount

router = APIRouter(prefix="/promo", tags=["promo"])


@router.post("/validate", response_model=PromoValidateResponse)
def validate_promo(payload: PromoValidateRequest, db: Session = Depends(get_db)):
    # build subtotal from cart
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

    res = calculate_discount(db, payload.code, subtotal)
    return PromoValidateResponse(valid=res.valid, discount=res.discount, reason=res.reason)
