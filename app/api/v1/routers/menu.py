from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
import os

from app.db.session import get_db
from app import models
from app.core.security import require_admin
from app.schemas.menu import CategoryOut, CategoryCreate, CategoryUpdate, MenuItemOut, MenuItemCreate, MenuItemUpdate
from app.schemas.admin import ImageUploadResponse, MenuItemImageUpdate
from app.services.images.processor import image_processor
from app.services.locale.locale_helper import get_localized_category_name, get_localized_menu_item_name, get_localized_menu_item_description

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(
    lc: str = Query("en", pattern="^(ru|kz|en)$"),
    db: Session = Depends(get_db)
):
    categories = db.query(models.Category).order_by(models.Category.sort.asc(), models.Category.name.asc()).all()
    
    # Apply localization
    for category in categories:
        category.name = get_localized_category_name(category, lc)
    
    return categories


@router.get("/items", response_model=List[MenuItemOut])
def list_items(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    active: Optional[bool] = True,
    lc: str = Query("en", pattern="^(ru|kz|en)$"),
    db: Session = Depends(get_db),
):
    q = db.query(models.MenuItem)
    if category_id is not None:
        q = q.filter(models.MenuItem.category_id == category_id)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(models.MenuItem.name.ilike(like), models.MenuItem.description.ilike(like)))
    if active is True:
        q = q.filter(models.MenuItem.is_active.is_(True))
    elif active is False:
        q = q.filter(models.MenuItem.is_active.is_(False))
    q = q.order_by(models.MenuItem.id.desc())
    
    items = q.all()
    
    # Apply localization
    for item in items:
        item.name = get_localized_menu_item_name(item, lc)
        item.description = get_localized_menu_item_description(item, lc)
    
    return items


@router.get("/items/{item_id}", response_model=MenuItemOut)
def get_item(item_id: int, lc: str = Query("en", pattern="^(ru|kz|en)$"), db: Session = Depends(get_db)):
    item = db.get(models.MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Apply localization
    item.name = get_localized_menu_item_name(item, lc)
    item.description = get_localized_menu_item_description(item, lc)
    
    return item


# Category CRUD operations (Admin only)

@router.post("/categories", response_model=CategoryOut)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    """Create a new category"""
    # Check for duplicate name
    existing = db.query(models.Category).filter(models.Category.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    
    category = models.Category(
        name=payload.name,
        sort=payload.sort
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    """Update a category"""
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check for duplicate name if name is being changed
    if payload.name and payload.name != category.name:
        existing = db.query(models.Category).filter(
            models.Category.name == payload.name,
            models.Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        category.name = payload.name
    
    if payload.sort is not None:
        category.sort = payload.sort
    
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    """Delete a category"""
    category = db.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has menu items
    items_count = db.query(models.MenuItem).filter(models.MenuItem.category_id == category_id).count()
    if items_count > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category with existing menu items")
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}


# Menu Item CRUD operations (Admin only)

@router.post("/items", response_model=MenuItemOut)
def create_menu_item(
    payload: MenuItemCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    """Create a new menu item"""
    # Validate category exists if provided
    if payload.category_id:
        category = db.get(models.Category, payload.category_id)
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    menu_item = models.MenuItem(
        category_id=payload.category_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        image_url=payload.image_url,
        is_active=payload.is_active
    )
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item


@router.put("/items/{item_id}", response_model=MenuItemOut)
def update_menu_item(
    item_id: int,
    payload: MenuItemUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    """Update a menu item"""
    menu_item = db.get(models.MenuItem, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Validate category exists if being changed
    if payload.category_id is not None:
        if payload.category_id:  # if not None and not 0
            category = db.get(models.Category, payload.category_id)
            if not category:
                raise HTTPException(status_code=400, detail="Category not found")
        menu_item.category_id = payload.category_id
    
    if payload.name is not None:
        menu_item.name = payload.name
    if payload.description is not None:
        menu_item.description = payload.description
    if payload.price is not None:
        menu_item.price = payload.price
    if payload.image_url is not None:
        menu_item.image_url = payload.image_url
    if payload.is_active is not None:
        menu_item.is_active = payload.is_active
    
    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)
    return menu_item


@router.delete("/items/{item_id}")
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    """Delete a menu item"""
    menu_item = db.get(models.MenuItem, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    # Check if item is in any orders (optional business logic)
    # For now, we'll allow deletion but could add this check later
    
    db.delete(menu_item)
    db.commit()
    return {"message": "Menu item deleted successfully"}


# Image upload endpoints (Admin only)

@router.post("/images/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    _: models.User = Depends(require_admin)
):
    """Upload and process an image file for menu items.
    
    Automatically converts images to webp format and returns the URL.
    Supports: jpg, jpeg, png, gif, bmp, tiff, webp formats.
    Maximum file size: 10MB.
    Maximum dimensions: 2048x2048 (automatically resized if larger).
    """
    try:
        # Process the image
        filename, file_path = await image_processor.process_image(file)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Generate URL (assuming images are served from /static/images/)
        image_url = f"/static/images/{filename}"
        
        return ImageUploadResponse(
            filename=filename,
            image_url=image_url,
            original_filename=file.filename,
            size_bytes=file_size
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@router.put("/items/{item_id}/image", response_model=MenuItemOut)
async def update_menu_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    """Upload and set image for a specific menu item.
    
    Processes the uploaded image and automatically updates the menu item's image_url.
    """
    # Check if menu item exists
    menu_item = db.get(models.MenuItem, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    try:
        # Store old image URL to potentially delete old file
        old_image_url = menu_item.image_url
        
        # Process the new image
        filename, file_path = await image_processor.process_image(file)
        
        # Generate new URL
        new_image_url = f"/static/images/{filename}"
        
        # Update menu item
        menu_item.image_url = new_image_url
        db.add(menu_item)
        db.commit()
        db.refresh(menu_item)
        
        # Optionally delete old image file (if it exists and was generated by us)
        if old_image_url and old_image_url.startswith("/static/images/"):
            old_filename = old_image_url.replace("/static/images/", "")
            image_processor.delete_image(old_filename)
        
        return menu_item
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update menu item image: {str(e)}")


@router.delete("/items/{item_id}/image")
def remove_menu_item_image(
    item_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin)
):
    """Remove image from a menu item."""
    menu_item = db.get(models.MenuItem, item_id)
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    old_image_url = menu_item.image_url
    
    # Remove image URL from database
    menu_item.image_url = None
    db.add(menu_item)
    db.commit()
    
    # Optionally delete the file (if it was generated by us)
    if old_image_url and old_image_url.startswith("/static/images/"):
        old_filename = old_image_url.replace("/static/images/", "")
        image_processor.delete_image(old_filename)
    
    return {"message": "Image removed from menu item successfully"}
