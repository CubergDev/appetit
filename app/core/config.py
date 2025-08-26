import os
from typing import List
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()


class Settings:
    # app
    APP_ENV: str = os.getenv("APP_ENV", "dev")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_me_very_long")
    ACCESS_TOKEN_EXPIRES_MIN: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "1440"))

    # CORS
    _origins_raw: str = os.getenv("ALLOWED_ORIGINS", "*")
    ALLOWED_ORIGINS: List[str] = [o.strip() for o in _origins_raw.split(",") if o.strip()] if _origins_raw else ["*"]

    # db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+pysqlite:///./app.db")

    # email / Resend
    RESEND_API_KEY: str | None = os.getenv("RESEND_API_KEY")
    FROM_EMAIL: str | None = os.getenv("FROM_EMAIL")
    FROM_NAME: str = os.getenv("FROM_NAME", "APPETIT")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    EMAIL_VERIFICATION_EXPIRES_MIN: int = int(os.getenv("EMAIL_VERIFICATION_EXPIRES_MIN", "30"))
    RESEND_WEBHOOK_SECRET: str | None = os.getenv("RESEND_WEBHOOK_SECRET")

    # push / Firebase
    GOOGLE_APPLICATION_CREDENTIALS: str | None = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    FCM_PROJECT_ID: str | None = os.getenv("FCM_PROJECT_ID")

    # maps
    GOOGLE_MAPS_API_KEY_SERVER: str | None = os.getenv("GOOGLE_MAPS_API_KEY_SERVER")

    # ga4
    GA_MEASUREMENT_ID: str | None = os.getenv("GA_MEASUREMENT_ID")
    GA_API_SECRET: str | None = os.getenv("GA_API_SECRET")

    # admin notifications
    ADMIN_EMAILS: List[str] = [e.strip() for e in os.getenv("ADMIN_EMAILS", "").split(",") if e.strip()]

    # pos / Payments
    POS_PROVIDER: str = os.getenv("POS_PROVIDER", "mock")
    POS_TIMEOUT_SECONDS: int = int(os.getenv("POS_TIMEOUT_SECONDS", "5"))
    PAYMENTS_PROVIDER: str = os.getenv("PAYMENTS_PROVIDER", "mock")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "whsec_dev")


settings = Settings()