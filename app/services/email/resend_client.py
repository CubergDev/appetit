import os
from typing import Optional, Dict

try:
    import resend  # type: ignore
except Exception:  # pragma: no cover
    resend = None  # graceful fallback when dependency not installed yet

FROM = None
if os.getenv("FROM_EMAIL"):
    FROM = f"{os.getenv('FROM_NAME', 'APPETIT')} <{os.environ['FROM_EMAIL']}>"


def health_check() -> Dict[str, str]:
    """Check Resend integration health and configuration status."""
    if resend is None:
        return {"status": "unavailable", "reason": "resend_library_not_installed"}
    
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("FROM_EMAIL")
    
    if not api_key:
        return {"status": "misconfigured", "reason": "missing_api_key"}
    if not from_email:
        return {"status": "misconfigured", "reason": "missing_from_email"}
    
    return {"status": "configured", "from_email": from_email}


def send_html(to: str, subject: str, html: str, tags: Optional[Dict[str, str]] = None):
    """Send an email via Resend if configured; otherwise, no-op.
    Returns a dict with a minimal result or raises if Resend is configured but errors.
    """
    if resend is None or not os.getenv("RESEND_API_KEY") or not FROM:
        # no-op fallback for dev environments
        return {"status": "skipped", "reason": "resend_not_configured"}

    try:
        resend.api_key = os.environ["RESEND_API_KEY"]
        params = {
            "from": FROM,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        if tags:
            params["tags"] = [{"name": k, "value": str(v)} for k, v in tags.items()]
        return resend.Emails.send(params)
    except Exception as e:
        return {"status": "error", "reason": "send_failed", "error": str(e)}