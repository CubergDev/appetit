from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.security import require_admin
from app.db.session import get_db
from app import models

router = APIRouter(prefix="/admin/analytics", tags=["admin"])


@router.get("/summary")
def summary(
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    q = db.query(models.Order)
    if from_:
        try:
            dt_from = datetime.fromisoformat(from_)
            q = q.filter(models.Order.created_at >= dt_from)
        except Exception:
            pass
    if to:
        try:
            dt_to = datetime.fromisoformat(to)
            q = q.filter(models.Order.created_at <= dt_to)
        except Exception:
            pass

    count = q.count()
    total_sum = db.query(func.coalesce(func.sum(models.Order.total), 0)).scalar() if count else 0
    # if filtered, compute sum on filtered q
    if from_ or to:
        total_sum = q.with_entities(func.coalesce(func.sum(models.Order.total), 0)).scalar()

    revenue = float(total_sum or 0)
    avg_order = round(revenue / count, 2) if count else 0.0
    return {
        "orders": int(count),
        "revenue": round(revenue, 2),
        "avg_order": avg_order,
    }
