import os
import hmac
import hashlib
import base64
import json
import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, Depends, status
from dotenv import load_dotenv
from database import verify_user_credentials

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin@transearch.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "transearch2025")
JWT_SECRET = os.getenv("JWT_SECRET", "transearch-executive-secret-key-2025-secure")

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4)) if len(data) % 4 != 0 else ''
    return base64.urlsafe_b64decode(data + padding)

def verify_credentials(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Check username and password against MongoDB users collection or default admin credentials."""
    return verify_user_credentials(username, password)

def create_access_token(username: str = "admin@transearch.com", role: str = "superadmin") -> str:
    """Create signed HMAC-SHA256 session token valid for 7 days."""
    payload = {
        "username": username,
        "role": role,
        "issuedAt": int(time.time() * 1000),
        "expiresAt": int((time.time() + 7 * 24 * 3600) * 1000)
    }
    payload_bytes = json.dumps(payload).encode('utf-8')
    payload_b64 = base64url_encode(payload_bytes)

    sig = hmac.new(JWT_SECRET.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
    sig_b64 = base64url_encode(sig)

    return f"{payload_b64}.{sig_b64}"

def verify_token(token: Optional[str]) -> Optional[Dict[str, Any]]:
    """Verify signed session token."""
    if not token:
        return None
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_b64, sig_b64 = parts

        expected_sig = hmac.new(JWT_SECRET.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).digest()
        expected_sig_b64 = base64url_encode(expected_sig)

        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return None

        decoded_bytes = base64url_decode(payload_b64)
        payload = json.loads(decoded_bytes.decode('utf-8'))

        # Check expiration
        now_ms = int(time.time() * 1000)
        if now_ms > payload.get("expiresAt", 0):
            return None

        return payload
    except Exception:
        return None

def get_current_admin(request: Request) -> Dict[str, Any]:
    """Dependency for securing admin endpoints."""
    # 1. Check Authorization Bearer header
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    # 2. Check cookie if header not provided
    if not token:
        token = request.cookies.get("transearch_admin_session")

    # 3. Check query param fallback
    if not token:
        token = request.query_params.get("token")

    session = verify_token(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized. Access is restricted to authenticated TRANSEARCH consultants."
        )
    return session
