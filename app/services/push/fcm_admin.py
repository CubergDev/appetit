import os
from typing import Optional, Dict

try:
    import firebase_admin  # type: ignore
    from firebase_admin import credentials, messaging  # type: ignore
except Exception:  # pragma: no cover
    firebase_admin = None
    credentials = None
    messaging = None

_initialized = False


def _ensure_init():
    global _initialized
    if _initialized:
        return
    if firebase_admin is None or credentials is None:
        return
    try:
        if not firebase_admin._apps:  # type: ignore
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not cred_path or not os.path.exists(cred_path):
                return
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        _initialized = True
    except Exception:
        # leave uninitd for graceful no-op
        _initialized = False


def health_check() -> Dict[str, str]:
    """Check FCM integration health and configuration status."""
    if firebase_admin is None or credentials is None:
        return {"status": "unavailable", "reason": "firebase_library_not_installed"}
    
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("FCM_PROJECT_ID")
    
    if not cred_path:
        return {"status": "misconfigured", "reason": "missing_credentials_path"}
    if not os.path.exists(cred_path):
        return {"status": "misconfigured", "reason": "credentials_file_not_found"}
    if not project_id:
        return {"status": "misconfigured", "reason": "missing_project_id"}
    
    _ensure_init()
    if not _initialized:
        return {"status": "error", "reason": "initialization_failed"}
    
    return {"status": "configured", "project_id": project_id, "credentials_file": cred_path}


def send_to_token(token: str, title: str, body: str, data: Optional[Dict[str, str]] = None):
    _ensure_init()
    if messaging is None or not _initialized:
        return {"status": "skipped", "reason": "fcm_not_configured"}
    msg = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in (data or {}).items()},
    )
    try:
        message_id = messaging.send(msg)
        return {"status": "sent", "id": message_id}
    except Exception as e:
        return {"status": "error", "reason": "send_failed", "error": str(e)}
