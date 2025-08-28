from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_admin
from app.db.session import get_db
from app import models
from app.schemas.modifications import (
    ModificationTypeOut,
    ModificationTypeIn,
    BulkModificationRequest,
    SingleModificationRequest,
    ModificationResponse,
    OrderItemModificationOut,
)
from app.services.locale.locale_helper import get_localized_modification_type_name

router = APIRouter(prefix="/modifications", tags=["modifications"])


# CRUD endpoints for modification types
@router.get("/types", response_model=List[ModificationTypeOut])
def get_modification_types(
    category: str = Query(None, description="Filter by category: sauce or removal"),
    is_active: bool = Query(True, description="Filter by active status"),
    lc: str = Query("en", pattern="^(ru|kz|en)$"),
    db: Session = Depends(get_db),
):
    """Get all available modification types"""
    query = db.query(models.ModificationType)
    
    if category:
        query = query.filter(models.ModificationType.category == category)
    
    query = query.filter(models.ModificationType.is_active == is_active)
    
    modification_types = query.order_by(models.ModificationType.name).all()
    
    # Apply localization
    for mod_type in modification_types:
        mod_type.name = get_localized_modification_type_name(mod_type, lc)
    
    return modification_types


@router.post("/types", response_model=ModificationTypeOut)
def create_modification_type(
    payload: ModificationTypeIn,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    """Create a new modification type (admin only)"""
    modification_type = models.ModificationType(**payload.dict())
    db.add(modification_type)
    db.commit()
    db.refresh(modification_type)
    return modification_type


@router.put("/types/{type_id}", response_model=ModificationTypeOut)
def update_modification_type(
    type_id: int,
    payload: ModificationTypeIn,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    """Update a modification type (admin only)"""
    modification_type = db.get(models.ModificationType, type_id)
    if not modification_type:
        raise HTTPException(status_code=404, detail="Modification type not found")
    
    for key, value in payload.dict().items():
        setattr(modification_type, key, value)
    
    db.commit()
    db.refresh(modification_type)
    return modification_type


@router.delete("/types/{type_id}")
def delete_modification_type(
    type_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    """Delete a modification type (admin only)"""
    modification_type = db.get(models.ModificationType, type_id)
    if not modification_type:
        raise HTTPException(status_code=404, detail="Modification type not found")
    
    db.delete(modification_type)
    db.commit()
    return {"message": "Modification type deleted successfully"}


# Single dish modification endpoints
@router.post("/single", response_model=ModificationResponse)
def apply_single_modification(
    payload: SingleModificationRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Apply modifications to a single order item"""
    # Verify order item exists and belongs to user
    order_item = db.get(models.OrderItem, payload.order_item_id)
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    order = db.get(models.Order, order_item.order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if order can still be modified (not delivered/cancelled)
    if order.status in ["DELIVERED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail="Cannot modify completed order")
    
    # Clear existing modifications for this order item
    db.query(models.OrderItemModification).filter(
        models.OrderItemModification.order_item_id == payload.order_item_id
    ).delete()
    
    # Apply new modifications
    for mod in payload.modifications:
        # Verify modification type exists
        mod_type = db.get(models.ModificationType, mod.modification_type_id)
        if not mod_type or not mod_type.is_active:
            raise HTTPException(status_code=400, detail=f"Invalid modification type: {mod.modification_type_id}")
        
        # Create modification
        order_mod = models.OrderItemModification(
            order_item_id=payload.order_item_id,
            modification_type_id=mod.modification_type_id,
            action=mod.action,
        )
        db.add(order_mod)
    
    db.commit()
    
    return ModificationResponse(
        success=True,
        message="Modifications applied successfully",
        modified_items=[payload.order_item_id]
    )


# Bulk modification endpoints
@router.post("/bulk", response_model=ModificationResponse)
def apply_bulk_modifications(
    payload: BulkModificationRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Apply modifications to multiple order items"""
    if not payload.order_item_ids:
        raise HTTPException(status_code=400, detail="Order item IDs required")
    
    # Verify all order items exist and belong to user
    order_items = db.query(models.OrderItem).filter(
        models.OrderItem.id.in_(payload.order_item_ids)
    ).all()
    
    if len(order_items) != len(payload.order_item_ids):
        raise HTTPException(status_code=404, detail="Some order items not found")
    
    # Verify all orders belong to user and can be modified
    order_ids = list(set(item.order_id for item in order_items))
    orders = db.query(models.Order).filter(models.Order.id.in_(order_ids)).all()
    
    for order in orders:
        if order.user_id != user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        if order.status in ["DELIVERED", "CANCELLED"]:
            raise HTTPException(status_code=400, detail=f"Cannot modify completed order {order.number}")
    
    modified_items = []
    
    for order_item_id in payload.order_item_ids:
        # Clear existing modifications for this order item
        db.query(models.OrderItemModification).filter(
            models.OrderItemModification.order_item_id == order_item_id
        ).delete()
        
        # Apply new modifications
        for mod in payload.modifications:
            # Verify modification type exists
            mod_type = db.get(models.ModificationType, mod.modification_type_id)
            if not mod_type or not mod_type.is_active:
                raise HTTPException(status_code=400, detail=f"Invalid modification type: {mod.modification_type_id}")
            
            # Create modification
            order_mod = models.OrderItemModification(
                order_item_id=order_item_id,
                modification_type_id=mod.modification_type_id,
                action=mod.action,
            )
            db.add(order_mod)
        
        modified_items.append(order_item_id)
    
    db.commit()
    
    return ModificationResponse(
        success=True,
        message=f"Modifications applied to {len(modified_items)} items",
        modified_items=modified_items
    )


@router.get("/order-item/{order_item_id}", response_model=List[OrderItemModificationOut])
def get_order_item_modifications(
    order_item_id: int,
    lc: str = Query("en", pattern="^(ru|kz|en)$"),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Get all modifications for a specific order item"""
    # Verify order item exists and belongs to user
    order_item = db.get(models.OrderItem, order_item_id)
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    order = db.get(models.Order, order_item.order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    modifications = db.query(models.OrderItemModification).filter(
        models.OrderItemModification.order_item_id == order_item_id
    ).all()
    
    # Apply localization to nested modification types
    for modification in modifications:
        if modification.modification_type:
            modification.modification_type.name = get_localized_modification_type_name(modification.modification_type, lc)
    
    return modifications


@router.delete("/order-item/{order_item_id}")
def clear_order_item_modifications(
    order_item_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Clear all modifications for a specific order item"""
    # Verify order item exists and belongs to user
    order_item = db.get(models.OrderItem, order_item_id)
    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    order = db.get(models.Order, order_item.order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if order can still be modified
    if order.status in ["DELIVERED", "CANCELLED"]:
        raise HTTPException(status_code=400, detail="Cannot modify completed order")
    
    # Delete all modifications for this order item
    deleted_count = db.query(models.OrderItemModification).filter(
        models.OrderItemModification.order_item_id == order_item_id
    ).delete()
    
    db.commit()
    
    return {"message": f"Cleared {deleted_count} modifications"}