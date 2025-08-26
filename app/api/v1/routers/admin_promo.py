import random
import string
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app import models
from app.schemas.admin import PromoGenerateRequest, PromoGenerateResponse

router = APIRouter(prefix="/admin/promo", tags=["admin"])


def _gen_code(prefix: str, length: int) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return prefix + "".join(random.choice(alphabet) for _ in range(length))


@router.post("/generate", response_model=PromoGenerateResponse)
def generate_promo(req: PromoGenerateRequest, db: Session = Depends(get_db), admin = Depends(require_admin)):
    if req.length <= 0 or req.count <= 0:
        raise HTTPException(status_code=400, detail="Invalid length or count")

    # create batch record
    batch = models.PromoBatch(prefix=req.prefix, length=req.length, count=req.count, created_by=admin.id)
    db.add(batch)
    db.commit()
    db.refresh(batch)

    created = 0
    attempts = 0
    max_attempts = req.count * 10
    while created < req.count and attempts < max_attempts:
        attempts += 1
        code = _gen_code(req.prefix, req.length)
        # try insert
        if db.get(models.Promocode, code):
            continue
        pc = models.Promocode(
            code=code,
            kind=req.kind,
            value=req.value,
            active=req.active,
            valid_from=req.valid_from,
            valid_to=req.valid_to,
            max_redemptions=req.max_redemptions,
            per_user_limit=req.per_user_limit,
            min_subtotal=req.min_subtotal,
            created_by=admin.id,
        )
        db.add(pc)
        try:
            db.commit()
            created += 1
        except Exception:
            db.rollback()
            # collision or other issue, continue trying
            continue

    return PromoGenerateResponse(batch_id=batch.id, generated=created, prefix=req.prefix, length=req.length)
