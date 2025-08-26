from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.api.v1.api import router as api_v1_router

app = FastAPI(title="APPETIT API", version="0.1.0")

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mount api
app.include_router(api_v1_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    # database managed by alembic
    # run 'alembic upgrade head' or scripts/init_db.py
    # startup hook for app-level init
    pass


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV}
