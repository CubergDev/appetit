import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Tuple

from app.core.config import settings


def generate_otp_data() -> Tuple[str, str, str, str, datetime]:
    """
    Generate OTP verification data.
    
    Returns:
        Tuple of (raw_token, raw_code, token_hash, code_hash, expires_at)
    """
    # Generate token (for potential future use) and 6-digit code
    raw_token = secrets.token_hex(16)
    raw_code = f"{secrets.randbelow(1000000):06d}"
    
    # Hash both for secure storage
    token_hash = _sha256(raw_token)
    code_hash = _sha256(raw_code)
    
    # Set expiration time
    expires_at = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.PHONE_VERIFICATION_EXPIRES_MIN
    )
    
    return raw_token, raw_code, token_hash, code_hash, expires_at


def hash_code(code: str) -> str:
    """Hash an OTP code for secure storage and verification."""
    return _sha256(code)


def _sha256(s: str) -> str:
    """Helper function to generate SHA256 hash."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def format_phone_number(phone: str) -> str:
    """
    Basic phone number formatting for consistency.
    Removes spaces, dashes, and ensures it starts with +.
    
    Args:
        phone: Raw phone number string
        
    Returns:
        Formatted phone number
    """
    # Remove common formatting characters
    clean = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Ensure it starts with +
    if not clean.startswith("+"):
        clean = "+" + clean
    
    return clean


def validate_phone_format(phone: str) -> bool:
    """
    Basic phone number validation.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if phone number appears valid
    """
    if not phone:
        return False
    
    # Clean the number
    clean = format_phone_number(phone)
    
    # Basic validation: should start with + and contain only digits after
    if not clean.startswith("+"):
        return False
    
    digits_only = clean[1:]  # Remove the +
    if not digits_only.isdigit():
        return False
    
    # Should be between 10-15 digits (international standards)
    if len(digits_only) < 10 or len(digits_only) > 15:
        return False
    
    return True