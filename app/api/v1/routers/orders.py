import random
from datetime import datetime
from uuid import uuid4
from typing import List
from decimal import Decimal

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
from app.services.locale.locale_helper import get_localized_menu_item_name, get_localized_modification_type_name
from app.services.business.hours import validate_business_hours
from app.services.analytics.ga4_streams import send_platform_event

router = APIRouter(prefix="/orders", tags=["orders"])


def _gen_order_number() -> str:
    # include timestamp and random suffix to avoid collisions
    return "ORD-" + datetime.utcnow().strftime("%y%m%d%H%M%S") + f"{random.randint(0, 999):03d}"


@router.post("", response_model=OrderOut)
def create_order(
    payload: OrderCreateRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not payload.items:
        raise HTTPException(status_code=400, detail="Items required")
    
    # Check business hours - reject orders during non-working hours
    hours_validation = validate_business_hours()
    if not hours_validation.is_open:
        error_messages = {
            "before_opening": "We are closed. Orders can only be placed during business hours.",
            "after_closing": "We are closed. Orders can only be placed during business hours.",
            "closed_today": "We are closed today.",
            "hours_not_configured": "Service temporarily unavailable.",
            "no_hours_defined": "Service temporarily unavailable."
        }
        error_msg = error_messages.get(hours_validation.reason, "We are currently closed.")
        
        if hours_validation.next_open_time:
            error_msg += f" We will be open again at {hours_validation.next_open_time.strftime('%Y-%m-%d %H:%M')}."
        
        raise HTTPException(status_code=400, detail=error_msg)

    item_ids = [it.item_id for it in payload.items]
    items_map = {m.id: m for m in db.query(models.MenuItem).filter(models.MenuItem.id.in_(item_ids)).all()}

    # Validate modifications if provided
    modification_types_map = {}
    if any(it.modifications for it in payload.items):
        all_mod_ids = set()
        for it in payload.items:
            if it.modifications:
                all_mod_ids.update(mod.modification_type_id for mod in it.modifications)
        
        if all_mod_ids:
            mod_types = db.query(models.ModificationType).filter(
                models.ModificationType.id.in_(all_mod_ids),
                models.ModificationType.is_active == True
            ).all()
            modification_types_map = {mt.id: mt for mt in mod_types}
            
            # Validate all modification types exist and are active
            for it in payload.items:
                if it.modifications:
                    for mod in it.modifications:
                        if mod.modification_type_id not in modification_types_map:
                            raise HTTPException(status_code=400, detail=f"Invalid modification type: {mod.modification_type_id}")

    subtotal = Decimal('0.0')
    lines = []
    for it in payload.items:
        mi = items_map.get(it.item_id)
        if not mi or not mi.is_active:
            raise HTTPException(status_code=400, detail=f"Invalid item: {it.item_id}")
        if it.qty <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        unit_price = Decimal(str(mi.price))  # Convert to Decimal for consistent calculations
        line_total = (unit_price * it.qty).quantize(Decimal('0.01'))
        subtotal += line_total
        lines.append((mi, it.qty, unit_price, it.modifications))

    promo_res = calculate_discount(db, payload.promocode, subtotal, user_id=user.id)
    discount = promo_res.discount if promo_res.valid else Decimal('0.0')
    total = max(Decimal('0.0'), subtotal - discount).quantize(Decimal('0.01'))

    order = models.Order(
        number=_gen_order_number(),
        user_id=user.id,
        fulfillment=payload.fulfillment,
        address_text=payload.address_text,
        lat=payload.lat,
        lng=payload.lng,
        status="NEW",
        subtotal=subtotal,
        discount=discount,
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

    # create order items and their modifications
    for mi, qty, unit_price, modifications in lines:
        order_item = models.OrderItem(
            order_id=order.id,
            item_id=mi.id,
            name_snapshot=mi.name,
            qty=qty,
            price_at_moment=unit_price,
        )
        db.add(order_item)
        db.flush()  # Flush to get the order_item.id
        
        # Create modifications for this order item
        if modifications:
            for mod in modifications:
                order_mod = models.OrderItemModification(
                    order_item_id=order_item.id,
                    modification_type_id=mod.modification_type_id,
                    action=mod.action,
                )
                db.add(order_mod)
    
    db.commit()
    db.refresh(order)

    # Auto-save address if delivery and address provided
    if (payload.fulfillment == "delivery" and payload.address_text and 
        payload.address_text.strip()):
        try:
            # Check if this address already exists for the user
            existing_address = db.query(models.SavedAddress).filter(
                models.SavedAddress.user_id == user.id,
                models.SavedAddress.address_text == payload.address_text.strip()
            ).first()
            
            if not existing_address:
                # Create new saved address
                saved_address = models.SavedAddress(
                    user_id=user.id,
                    address_text=payload.address_text.strip(),
                    latitude=payload.lat,
                    longitude=payload.lng,
                    label=None,  # Let user set label later if needed
                    is_default=False  # Don't auto-set as default
                )
                db.add(saved_address)
                db.commit()
        except Exception:
            # Don't fail order creation if address saving fails
            pass

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

    # GA4 analytics tracking (best-effort)
    try:
        # Prepare event parameters
        event_params = {
            "transaction_id": order.number,
            "value": float(order.total),
            "currency": "KZT",  # Adjust currency as needed
            "num_items": len(lines),
            "fulfillment_type": order.fulfillment,
            "payment_method": order.payment_method,
        }
        
        # Add UTM parameters if available
        if order.utm_source:
            event_params["utm_source"] = order.utm_source
        if order.utm_medium:
            event_params["utm_medium"] = order.utm_medium
        if order.utm_campaign:
            event_params["utm_campaign"] = order.utm_campaign
            
        # Add promocode if used
        if order.promocode_code:
            event_params["coupon"] = order.promocode_code
            event_params["discount"] = float(order.discount)
            
        # Determine client_id (GA client ID from payload or fallback to user-based ID)
        client_id = payload.ga_client_id or f"user_{user.id}"
        
        # Send purchase event to all configured platforms
        platforms_to_track = ["web", "android", "ios"]
        for platform in platforms_to_track:
            send_platform_event(
                platform=platform,
                name="purchase",
                client_id=client_id,
                params=event_params
            )
    except Exception:
        # Don't fail order creation if analytics fails
        pass

    return order


@router.get("/mine", response_model=OrderListResponse)
def my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    lc: str = Query("en", pattern="^(ru|kz|en)$"),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    q = (
        db.query(models.Order)
        .filter(models.Order.user_id == user.id)
        .order_by(models.Order.created_at.desc())
    )
    orders = q.offset((page - 1) * page_size).limit(page_size).all()
    
    # Apply localization to order items
    for order in orders:
        _ = order.items  # trigger load
        for order_item in order.items:
            if order_item.menu_item:
                order_item.menu_item.name = get_localized_menu_item_name(order_item.menu_item, lc)
            for modification in order_item.modifications:
                if modification.modification_type:
                    modification.modification_type.name = get_localized_modification_type_name(modification.modification_type, lc)
    
    return OrderListResponse(items=orders)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, lc: str = Query("en", pattern="^(ru|kz|en)$"), db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    order = db.get(models.Order, order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Apply localization to order items
    _ = order.items  # trigger load
    for order_item in order.items:
        if order_item.menu_item:
            order_item.menu_item.name = get_localized_menu_item_name(order_item.menu_item, lc)
        for modification in order_item.modifications:
            if modification.modification_type:
                modification.modification_type.name = get_localized_modification_type_name(modification.modification_type, lc)
    
    return order


