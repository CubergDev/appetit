from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app import models


class PromoValidationResult:
    def __init__(self, valid: bool, discount: float = 0.0, reason: Optional[str] = None):
        self.valid = valid
        self.discount = float(discount)
        self.reason = reason

    def dict(self):
        return {"valid": self.valid, "discount": self.discount, "reason": self.reason}


def calculate_discount(db: Session, code: Optional[str], subtotal: float, user_id: Optional[int] = None) -> PromoValidationResult:
    if not code:
        return PromoValidationResult(valid=True, discount=0.0)

    promo: models.Promocode | None = db.get(models.Promocode, code)
    if not promo or not promo.active:
        return PromoValidationResult(valid=False, reason="invalid_or_inactive")

    now = datetime.utcnow()
    if promo.valid_from and now < promo.valid_from:
        return PromoValidationResult(valid=False, reason="not_started")
    if promo.valid_to and now > promo.valid_to:
        return PromoValidationResult(valid=False, reason="expired")

    if promo.min_subtotal is not None and subtotal < float(promo.min_subtotal):
        return PromoValidationResult(valid=False, reason="min_subtotal_not_met")

    # note: max_redemptions and per_user_limit are not tracked in MVP without redemption logs
    # apply discount
    discount = 0.0
    if promo.kind == "percent":
        discount = round(subtotal * float(promo.value) / 100.0, 2)
    elif promo.kind == "amount":
        discount = float(promo.value)

    # ensure non-negative total
    discount = min(discount, subtotal)
    return PromoValidationResult(valid=True, discount=discount)