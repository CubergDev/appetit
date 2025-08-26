from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app import models
from app.schemas.orders import OrderOut
from app.schemas.admin import StatusUpdateRequest

router = APIRouter(prefix="/admin/orders", tags=["admin"])


@router.get("", response_model=List[OrderOut])
def list_orders(
    status: Optional[str] = Query(None),
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    q = db.query(models.Order)
    if status:
        q = q.filter(models.Order.status == status)
    # parse ISO timestamps if provided
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
    q = q.order_by(models.Order.created_at.desc())
    orders = q.all()
    for o in orders:
        _ = o.items
    return orders


@router.get("/{order_id}", response_model=OrderOut)
def get_order_admin(order_id: int, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    _ = order.items
    return order


ALLOWED_STATUSES = {"NEW", "COOKING", "ON_WAY", "DELIVERED", "CANCELLED"}


@router.put("/{order_id}/status", response_model=OrderOut)
def update_order_status(order_id: int, payload: StatusUpdateRequest, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    if payload.status not in ALLOWED_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    order = db.get(models.Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = payload.status
    db.add(order)
    db.commit()
    db.refresh(order)
    _ = order.items
    return order
