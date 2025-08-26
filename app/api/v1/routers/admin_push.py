from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import require_admin
from app.db.session import get_db
from app import models
from app.schemas.admin import AdminPushRequest, AdminPushResponse
from app.services.push.fcm_admin import send_to_token

router = APIRouter(prefix="/admin/push", tags=["admin"]) 


@router.post("/send", response_model=AdminPushResponse)
def send_push(req: AdminPushRequest, db: Session = Depends(get_db), _: models.User = Depends(require_admin)):
    # currently only audience="all" is supported
    tokens: List[str] = [d.fcm_token for d in db.query(models.Device).all()]
    sent = 0
    for token in tokens:
        try:
            res = send_to_token(token, title=req.title, body=req.body)
            if isinstance(res, dict) and res.get("status") == "sent":
                sent += 1
        except Exception:
            # ignore individual failures in MVP
            pass
    return AdminPushResponse(sent=sent)
