from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app import models
from app.schemas.menu import CategoryOut, MenuItemOut

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    q = db.query(models.Category).order_by(models.Category.sort.asc(), models.Category.name.asc())
    return q.all()


@router.get("/items", response_model=List[MenuItemOut])
def list_items(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    active: Optional[bool] = True,
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
    return q.all()


@router.get("/items/{item_id}", response_model=MenuItemOut)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
