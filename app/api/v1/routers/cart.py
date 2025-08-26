from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app import models
from app.schemas.promo_cart import PriceRequest, PriceResponse, PriceDetailsLine
from app.services.promo.validator import calculate_discount

router = APIRouter(prefix="/cart", tags=["cart"]) 


@router.post("/price", response_model=PriceResponse)
def calculate_price(payload: PriceRequest, db: Session = Depends(get_db)):
    if not payload.items:
        return PriceResponse(subtotal=0.0, discount=0.0, total=0.0, details=[])

    item_ids = [ci.item_id for ci in payload.items]
    items = {m.id: m for m in db.query(models.MenuItem).filter(models.MenuItem.id.in_(item_ids)).all()}

    details: List[PriceDetailsLine] = []
    subtotal = 0.0
    for ci in payload.items:
        mi = items.get(ci.item_id)
        if not mi or not mi.is_active:
            raise HTTPException(status_code=400, detail=f"Invalid item in cart: {ci.item_id}")
        if ci.qty <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        unit_price = float(mi.price)
        line_total = round(unit_price * ci.qty, 2)
        subtotal += line_total
        details.append(
            PriceDetailsLine(
                item_id=ci.item_id,
                name=mi.name,
                qty=ci.qty,
                unit_price=unit_price,
                line_total=line_total,
            )
        )

    promo_res = calculate_discount(db, payload.promocode, subtotal)
    discount = float(promo_res.discount if promo_res.valid else 0.0)
    total = round(max(0.0, subtotal - discount), 2)
    return PriceResponse(subtotal=round(subtotal, 2), discount=round(discount, 2), total=total, details=details)