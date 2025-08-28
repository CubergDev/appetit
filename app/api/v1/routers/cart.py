from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.core.security import get_current_user
from app.db.session import get_db
from app import models
from app.schemas.promo_cart import PriceRequest, PriceResponse, PriceDetailsLine
from app.schemas.cart import (
    CartOut, AddToCartRequest, UpdateCartItemRequest, 
    CartItemResponse, CartResponse, CartPriceRequest, CartPriceResponse
)
from app.services.promo.validator import calculate_discount

router = APIRouter(prefix="/cart", tags=["cart"]) 


def get_or_create_cart(user_id: int, db: Session) -> models.Cart:
    """Get existing cart or create a new one for the user."""
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        cart = models.Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def calculate_cart_totals(cart: models.Cart) -> dict:
    """Calculate cart totals and item details."""
    subtotal = Decimal('0.0')
    total_items = 0
    
    for cart_item in cart.items:
        if cart_item.menu_item and cart_item.menu_item.is_active:
            line_total = Decimal(str(cart_item.menu_item.price)) * cart_item.qty
            subtotal += line_total
            total_items += cart_item.qty
    
    return {
        'subtotal': float(subtotal),
        'total_items': total_items
    }


@router.get("/", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Get current user's cart."""
    cart = get_or_create_cart(user.id, db)
    
    # Calculate totals
    totals = calculate_cart_totals(cart)
    
    # Build response
    cart_items = []
    for cart_item in cart.items:
        if cart_item.menu_item and cart_item.menu_item.is_active:
            line_total = float(Decimal(str(cart_item.menu_item.price)) * cart_item.qty)
            
            modifications = []
            for mod in cart_item.modifications:
                modifications.append({
                    "id": mod.id,
                    "modification_type_id": mod.modification_type_id,
                    "modification_name": mod.modification_type.name,
                    "action": mod.action
                })
            
            cart_items.append({
                "id": cart_item.id,
                "item_id": cart_item.item_id,
                "item_name": cart_item.menu_item.name,
                "item_price": float(cart_item.menu_item.price),
                "qty": cart_item.qty,
                "line_total": line_total,
                "modifications": modifications,
                "created_at": cart_item.created_at,
                "updated_at": cart_item.updated_at
            })
    
    cart_response = {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": cart_items,
        "subtotal": totals['subtotal'],
        "total_items": totals['total_items'],
        "created_at": cart.created_at,
        "updated_at": cart.updated_at
    }
    
    return CartResponse(message="Cart retrieved successfully", cart=cart_response)


@router.post("/add", response_model=CartItemResponse)
def add_to_cart(
    payload: AddToCartRequest, 
    db: Session = Depends(get_db), 
    user: models.User = Depends(get_current_user)
):
    """Add item to cart."""
    # Validate menu item
    menu_item = db.query(models.MenuItem).filter(models.MenuItem.id == payload.item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    if not menu_item.is_active:
        raise HTTPException(status_code=400, detail="Menu item is not available")
    
    if payload.qty <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    # Get or create cart
    cart = get_or_create_cart(user.id, db)
    
    # Check if item already exists in cart
    existing_item = db.query(models.CartItem).filter(
        models.CartItem.cart_id == cart.id,
        models.CartItem.item_id == payload.item_id
    ).first()
    
    if existing_item:
        # Update quantity
        existing_item.qty += payload.qty
        db.add(existing_item)
        cart_item = existing_item
    else:
        # Create new cart item
        cart_item = models.CartItem(
            cart_id=cart.id,
            item_id=payload.item_id,
            qty=payload.qty
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    
    # Add modifications if provided
    for mod_data in payload.modifications:
        # Validate modification type
        mod_type = db.query(models.ModificationType).filter(
            models.ModificationType.id == mod_data.get("modification_type_id")
        ).first()
        if mod_type and mod_type.is_active:
            cart_mod = models.CartItemModification(
                cart_item_id=cart_item.id,
                modification_type_id=mod_data.get("modification_type_id"),
                action=mod_data.get("action", "add")
            )
            db.add(cart_mod)
    
    db.commit()
    db.refresh(cart_item)
    
    return CartItemResponse(message="Item added to cart successfully", cart_item=None)


@router.put("/item/{cart_item_id}", response_model=CartItemResponse)
def update_cart_item(
    cart_item_id: int,
    payload: UpdateCartItemRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Update cart item quantity and modifications."""
    # Get user's cart
    cart = get_or_create_cart(user.id, db)
    
    # Find cart item
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id,
        models.CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    if payload.qty <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    
    # Update quantity
    cart_item.qty = payload.qty
    db.add(cart_item)
    
    # Update modifications if provided
    if payload.modifications is not None:
        # Clear existing modifications
        db.query(models.CartItemModification).filter(
            models.CartItemModification.cart_item_id == cart_item.id
        ).delete()
        
        # Add new modifications
        for mod_data in payload.modifications:
            mod_type = db.query(models.ModificationType).filter(
                models.ModificationType.id == mod_data.get("modification_type_id")
            ).first()
            if mod_type and mod_type.is_active:
                cart_mod = models.CartItemModification(
                    cart_item_id=cart_item.id,
                    modification_type_id=mod_data.get("modification_type_id"),
                    action=mod_data.get("action", "add")
                )
                db.add(cart_mod)
    
    db.commit()
    db.refresh(cart_item)
    
    return CartItemResponse(message="Cart item updated successfully", cart_item=None)


@router.delete("/item/{cart_item_id}", response_model=CartItemResponse)
def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Remove item from cart."""
    # Get user's cart
    cart = get_or_create_cart(user.id, db)
    
    # Find and delete cart item
    cart_item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id,
        models.CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    
    return CartItemResponse(message="Item removed from cart successfully", cart_item=None)


@router.delete("/clear", response_model=CartResponse)
def clear_cart(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Clear all items from cart."""
    cart = get_or_create_cart(user.id, db)
    
    # Delete all cart items
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
    db.commit()
    
    # Return empty cart
    cart_response = {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": [],
        "subtotal": 0.0,
        "total_items": 0,
        "created_at": cart.created_at,
        "updated_at": cart.updated_at
    }
    
    return CartResponse(message="Cart cleared successfully", cart=cart_response)


@router.post("/price", response_model=CartPriceResponse)
def calculate_cart_price(
    payload: CartPriceRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    """Calculate cart price with optional promo code."""
    cart = get_or_create_cart(user.id, db)
    
    if not cart.items:
        return CartPriceResponse(
            subtotal=0.0,
            discount=0.0,
            total=0.0,
            promocode_valid=False,
            promocode_message="Cart is empty"
        )
    
    # Calculate subtotal
    subtotal = Decimal('0.0')
    for cart_item in cart.items:
        if cart_item.menu_item and cart_item.menu_item.is_active:
            line_total = Decimal(str(cart_item.menu_item.price)) * cart_item.qty
            subtotal += line_total
    
    # Apply promo code if provided
    discount = Decimal('0.0')
    promocode_valid = False
    promocode_message = None
    
    if payload.promocode:
        promo_res = calculate_discount(db, payload.promocode, subtotal)
        if promo_res.valid:
            discount = promo_res.discount
            promocode_valid = True
            promocode_message = "Promo code applied successfully"
        else:
            promocode_message = promo_res.reason or "Invalid promo code"
    
    total = max(Decimal('0.0'), subtotal - discount)
    
    return CartPriceResponse(
        subtotal=float(subtotal),
        discount=float(discount),
        total=float(total),
        promocode_valid=promocode_valid,
        promocode_message=promocode_message
    )


@router.post("/price-legacy", response_model=PriceResponse)
def calculate_price(payload: PriceRequest, db: Session = Depends(get_db)):
    if not payload.items:
        return PriceResponse(subtotal=0.0, discount=0.0, total=0.0, details=[])

    item_ids = [ci.item_id for ci in payload.items]
    items = {m.id: m for m in db.query(models.MenuItem).filter(models.MenuItem.id.in_(item_ids)).all()}

    details: List[PriceDetailsLine] = []
    subtotal = Decimal('0.0')
    for ci in payload.items:
        mi = items.get(ci.item_id)
        if not mi or not mi.is_active:
            raise HTTPException(status_code=400, detail=f"Invalid item in cart: {ci.item_id}")
        if ci.qty <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        unit_price = Decimal(str(mi.price))  # Convert to Decimal for consistent calculations
        line_total = (unit_price * ci.qty).quantize(Decimal('0.01'))
        subtotal += line_total
        details.append(
            PriceDetailsLine(
                item_id=ci.item_id,
                name=mi.name,
                qty=ci.qty,
                unit_price=float(unit_price),  # Convert to float for API response
                line_total=float(line_total),  # Convert to float for API response
            )
        )

    promo_res = calculate_discount(db, payload.promocode, subtotal)
    discount = promo_res.discount if promo_res.valid else Decimal('0.0')
    total = max(Decimal('0.0'), subtotal - discount).quantize(Decimal('0.01'))
    return PriceResponse(subtotal=float(subtotal), discount=float(discount), total=float(total), details=details)