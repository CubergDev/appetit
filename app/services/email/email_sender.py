import os
import hashlib
from typing import Dict, Optional, Any
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

try:
    import resend  # type: ignore
except Exception:  # pragma: no cover
    resend = None  # graceful fallback when dependency not installed yet

FROM_EMAIL = os.getenv("FROM_EMAIL", "notify@example.com")
FROM_NAME = os.getenv("FROM_NAME", "MyApp")
APP_URL = os.getenv("APP_URL", "https://ium.app")

# template configs
TEMPLATES = {
    "verify_email": {
        "subject": "Verify your email address",
        "required_vars": ["user_name", "verify_url"],
        "optional_vars": ["otp"]
    },
    "order_created": {
        "subject": "Order #{order_id} created",
        "required_vars": ["order_id", "order_url", "pickup_or_delivery", "eta"],
        "optional_vars": []
    },
    "order_status": {
        "subject": "Order #{order_id} status update",
        "required_vars": ["order_id", "status", "eta"],
        "optional_vars": []
    },
    "order_delivered": {
        "subject": "Order #{order_id} delivered",
        "required_vars": ["order_id", "rating_url"],
        "optional_vars": []
    },
    "password_reset": {
        "subject": "Reset your password",
        "required_vars": ["reset_url"],
        "optional_vars": []
    }
}


def add_utm_parameters(url: str, template: str) -> str:
    """Add UTM parameters to a URL for email tracking."""
    if not url or not url.startswith(('http://', 'https://')):
        return url
    
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # add UTM parameters
    query_params['utm_source'] = ['email']
    query_params['utm_medium'] = ['transactional']
    query_params['utm_campaign'] = [template]
    
    # convert back to query string
    new_query = urlencode(query_params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def select_subject(template: str, variables: Dict[str, Any]) -> str:
    """Select and format subject line for a template."""
    if template not in TEMPLATES:
        return f"Notification from {FROM_NAME}"
    
    subject_template = TEMPLATES[template]["subject"]
    
    # simple variable substitution for subjects
    try:
        return subject_template.format(**variables)
    except (KeyError, ValueError):
        return subject_template


def render_template(template: str, variables: Dict[str, Any]) -> str:
    """Render HTML template with variables and UTM parameters."""
    # add UTM parameters to all URLs in variables
    enhanced_vars = variables.copy()
    for key, value in variables.items():
        if isinstance(value, str) and key.endswith('_url'):
            enhanced_vars[key] = add_utm_parameters(value, template)
    
    if template == "verify_email":
        user_name = enhanced_vars.get("user_name", "User")
        verify_url = enhanced_vars.get("verify_url", "#")
        otp = enhanced_vars.get("otp", "")
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Hello {user_name}!</h2>
            <p>Please verify your email address to complete your account setup.</p>
            {f'<p>Your verification code: <strong>{otp}</strong></p>' if otp else ''}
            <p><a href="{verify_url}" style="background: #007cba; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Verify Email</a></p>
            <p>If the button doesn't work, copy and paste this link: <a href="{verify_url}">{verify_url}</a></p>
        </div>
        """
        
    elif template == "order_created":
        order_id = enhanced_vars.get("order_id", "")
        order_url = enhanced_vars.get("order_url", "#")
        pickup_or_delivery = enhanced_vars.get("pickup_or_delivery", "pickup")
        eta = enhanced_vars.get("eta", "")
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Order #{order_id} Confirmed!</h2>
            <p>Thank you for your order. We're preparing it now.</p>
            <p><strong>Type:</strong> {pickup_or_delivery.title()}</p>
            <p><strong>Estimated time:</strong> {eta}</p>
            <p><a href="{order_url}" style="background: #007cba; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">View Order</a></p>
        </div>
        """
        
    elif template == "order_status":
        order_id = enhanced_vars.get("order_id", "")
        status = enhanced_vars.get("status", "")
        eta = enhanced_vars.get("eta", "")
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Order #{order_id} Update</h2>
            <p>Your order status has been updated to: <strong>{status.title()}</strong></p>
            <p><strong>Estimated time:</strong> {eta}</p>
        </div>
        """
        
    elif template == "order_delivered":
        order_id = enhanced_vars.get("order_id", "")
        rating_url = enhanced_vars.get("rating_url", "#")
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Order #{order_id} Delivered!</h2>
            <p>Your order has been successfully delivered. Thank you for choosing us!</p>
            <p>How was your experience?</p>
            <p><a href="{rating_url}" style="background: #007cba; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Rate Your Order</a></p>
        </div>
        """
        
    elif template == "password_reset":
        reset_url = enhanced_vars.get("reset_url", "#")
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Password Reset Request</h2>
            <p>You requested to reset your password. Click the button below to create a new password:</p>
            <p><a href="{reset_url}" style="background: #007cba; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Reset Password</a></p>
            <p>If you didn't request this, please ignore this email.</p>
            <p>If the button doesn't work, copy and paste this link: <a href="{reset_url}">{reset_url}</a></p>
        </div>
        """
    else:
        html = "<p>Email notification</p>"
    
    return html


def send_email(
    template: str, 
    to: str, 
    variables: Dict[str, Any], 
    user_id: Optional[int] = None, 
    idempotency_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send transactional email using Resend API.
    
    Args:
        template: Email template name (verify_email, order_created, etc.)
        to: Recipient email address
        variables: Template variables
        user_id: Optional user ID for tracking
        idempotency_key: Optional key for preventing duplicate sends
        
    Returns:
        Dict with result including message_id from Resend
    """
    if resend is None or not os.getenv("RESEND_API_KEY"):
        return {"status": "skipped", "reason": "resend_not_configured"}
    
    # validate template
    if template not in TEMPLATES:
        return {"status": "error", "reason": "invalid_template", "template": template}
    
    # validate required variables
    required_vars = TEMPLATES[template]["required_vars"]
    missing_vars = [var for var in required_vars if var not in variables]
    if missing_vars:
        return {"status": "error", "reason": "missing_variables", "missing": missing_vars}
    
    try:
        resend.api_key = os.environ["RESEND_API_KEY"]
        
        subject = select_subject(template, variables)
        html = render_template(template, variables)
        
        params = {
            "from": f"{FROM_NAME} <{FROM_EMAIL}>",
            "to": [to],
            "subject": subject,
            "html": html,
            "tags": [{"name": "category", "value": template}]
        }
        
        # add user_id tag if provided
        if user_id:
            params["tags"].append({"name": "user_id", "value": str(user_id)})
        
        result = resend.Emails.send(params)
        
        # extract message_id for idempotency tracking
        message_id = result.get("id") if isinstance(result, dict) else None
        
        return {
            "status": "sent",
            "message_id": message_id,
            "template": template,
            "recipient": to,
            "subject": subject
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "reason": "send_failed", 
            "error": str(e),
            "template": template,
            "recipient": to
        }


def send_html(to: str, subject: str, html: str, tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Send an email via Resend if configured; otherwise, no-op.
    Compatibility function matching resend_client.py interface.
    """
    if resend is None or not os.getenv("RESEND_API_KEY") or not FROM_EMAIL:
        # No-op fallback for dev environments
        return {"status": "skipped", "reason": "resend_not_configured"}

    try:
        resend.api_key = os.environ["RESEND_API_KEY"]
        params = {
            "from": f"{FROM_NAME} <{FROM_EMAIL}>",
            "to": [to],
            "subject": subject,
            "html": html,
        }
        if tags:
            params["tags"] = [{"name": k, "value": str(v)} for k, v in tags.items()]
        return resend.Emails.send(params)
    except Exception as e:
        return {"status": "error", "reason": "send_failed", "error": str(e)}


def health_check() -> Dict[str, str]:
    """Check email sender configuration and health."""
    if resend is None:
        return {"status": "unavailable", "reason": "resend_library_not_installed"}
    
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("FROM_EMAIL")
    
    if not api_key:
        return {"status": "misconfigured", "reason": "missing_api_key"}
    if not from_email:
        return {"status": "misconfigured", "reason": "missing_from_email"}
    
    return {"status": "configured", "from_email": from_email, "templates": len(TEMPLATES)}