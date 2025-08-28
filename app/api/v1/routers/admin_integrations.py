from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.core.security import require_admin
from app import models

router = APIRouter(prefix="/admin/integrations", tags=["admin"])


@router.get("/status")
def get_integrations_status(_: models.User = Depends(require_admin)):
    """Get status of all integrations for admin monitoring."""
    from app.services.email.email_sender import health_check as email_health
    from app.services.push.fcm_admin import health_check as push_health
    from app.services.sms.twilio_sender import health_check as sms_health
    from app.services.maps.google import health_check as maps_health
    from app.services.analytics.ga4_mp import health_check as ga4_health
    from app.services.analytics.ga4_streams import health_check_all as ga4_streams_health
    from app.services.pos.factory import get_pos_adapter
    from app.services.payments.mock import MockPayments
    
    # get health status for each integration
    status = {
        "email": email_health(),
        "push": push_health(),
        "sms": sms_health(),
        "maps": maps_health(),
        "analytics": ga4_health(),
        "analytics_streams": ga4_streams_health(),
        "pos": {
            "status": "configured",
            "provider": "mock",
            "note": "Using mock POS adapter"
        },
        "payments": {
            "status": "configured", 
            "provider": "mock",
            "note": "Using mock payment provider"
        }
    }
    
    # add overall summary
    configured_count = sum(1 for service in status.values() if isinstance(service, dict) and service.get("status") == "configured")
    total_count = len(status)
    
    return {
        "summary": {
            "configured": configured_count,
            "total": total_count,
            "all_ready": configured_count == total_count
        },
        "services": status
    }


@router.get("/ga4/health")
def ga4_health(_: models.User = Depends(require_admin)):
    """Return health status for GA4 streams (android, ios, web)."""
    from app.services.analytics.ga4_streams import health_check_all
    return health_check_all()


@router.post("/ga4/test-event")
def ga4_test_event(
    platform: Optional[str] = Query("all", description="android|ios|web|all"),
    event_name: str = Query("test_event"),
    client_id: Optional[str] = Query(None),
    _: models.User = Depends(require_admin),
):
    """Send a GA4 test event to a specific platform stream or all streams."""
    from datetime import datetime
    from app.services.analytics.ga4_streams import send_platform_event, SUPPORTED_PLATFORMS

    plat = (platform or "all").lower()
    sent_at = datetime.utcnow().isoformat() + "Z"

    if plat == "all":
        results = {
            p: send_platform_event(p, event_name, client_id=client_id or f"admin-test-{p}", params={"source": "admin"})
            for p in sorted(SUPPORTED_PLATFORMS)
        }
        return {"status": "ok", "sent_at": sent_at, "results": results}

    if plat not in SUPPORTED_PLATFORMS:
        return {"status": "error", "reason": "invalid_platform", "supported": sorted(SUPPORTED_PLATFORMS)}

    result = send_platform_event(plat, event_name, client_id=client_id or f"admin-test-{plat}", params={"source": "admin"})
    return {"status": "ok", "sent_at": sent_at, "platform": plat, "result": result}
