import random
from datetime import datetime
from uuid import uuid4
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app import models
from app.schemas.orders import (
    OrderCreateRequest,
    OrderOut,
    OrderListResponse,
)
from app.services.promo.validator import calculate_discount
from app.services.email.order_emails import send_order_created
from app.services.push.fcm_admin import send_to_token

router = APIRouter(prefix="/orders", tags=["orders"])


def _gen_order_number() -> str:
    # include timestamp and random suffix to avoid collisions
    return datetime.utcnow().strftime("%y%m%d%H%M%S") + f"{random.randint(0, 999999):06d}"


@router.post("", response_model=OrderOut)
def create_order(
    payload: OrderCreateRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Items required")

    item_ids = [it.item_id for it in payload.items]
    items_map = {m.id: m for m in db.query(models.MenuItem).filter(models.MenuItem.id.in_(item_ids)).all()}

    subtotal = 0.0
    lines = []
    for it in payload.items:
        mi = items_map.get(it.item_id)
        if not mi or not mi.is_active:
            raise HTTPException(status_code=400, detail=f"Invalid item: {it.item_id}")
        if it.qty <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        unit_price = float(mi.price)
        line_total = round(unit_price * it.qty, 2)
        subtotal += line_total
        lines.append((mi, it.qty, unit_price))

    promo_res = calculate_discount(db, payload.promocode, subtotal, user_id=user.id)
    discount = float(promo_res.discount if promo_res.valid else 0.0)
    total = round(max(0.0, subtotal - discount), 2)

    order = models.Order(
        number=_gen_order_number(),
        user_id=user.id,
        fulfillment=payload.fulfillment,
        address_text=payload.address_text,
        lat=payload.lat,
        lng=payload.lng,
        status="NEW",
        subtotal=round(subtotal, 2),
        discount=round(discount, 2),
        total=total,
        promocode_code=payload.promocode if promo_res.valid and payload.promocode else None,
        paid=False,
        payment_method=payload.payment_method or "cod",
        utm_source=payload.utm_source,
        utm_medium=payload.utm_medium,
        utm_campaign=payload.utm_campaign,
        ga_client_id=payload.ga_client_id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # create order items
    for mi, qty, unit_price in lines:
        db.add(
            models.OrderItem(
                order_id=order.id,
                item_id=mi.id,
                name_snapshot=mi.name,
                qty=qty,
                price_at_moment=unit_price,
            )
        )
    db.commit()
    db.refresh(order)

    # send email (best-effort)
    if user.email:
        try:
            send_order_created(to=user.email, order=order, user_id=user.id)
        except Exception:
            pass

    # push notifications (best-effort)
    devices: List[models.Device] = db.query(models.Device).filter(models.Device.user_id == user.id).all()
    for d in devices:
        try:
            send_to_token(d.fcm_token, title="Заказ принят", body=f"#{order.number} на {order.total}")
        except Exception:
            pass

    return order


@router.get("/mine", response_model=OrderListResponse)
def my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    q = (
        db.query(models.Order)
        .filter(models.Order.user_id == user.id)
        .order_by(models.Order.created_at.desc())
    )
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    # ensure items relationship loaded
    for o in items:
        _ = o.items  # trigger load
    return OrderListResponse(items=items)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = db.get(models.Order, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    _ = order.items
    return order


