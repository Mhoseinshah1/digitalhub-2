"""Web panel authentication.

Admin credentials come from ``.env`` (``WEB_ADMIN_USERNAME`` +
``WEB_ADMIN_PASSWORD_HASH``). The password is verified with bcrypt; a signed
JWT is issued and stored in an HttpOnly session cookie.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import Request
from jose import JWTError, jwt
from passlib.context import CryptContext

from shared.config import settings

COOKIE_NAME = "session"

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if ``plain`` matches the bcrypt ``hashed`` value."""
    try:
        return _pwd.verify(plain, hashed)
    except ValueError:
        return False


def authenticate_admin(username: str, password: str) -> bool:
    """Check submitted credentials against the configured admin."""
    if username != settings.WEB_ADMIN_USERNAME:
        return False
    return verify_password(password, settings.WEB_ADMIN_PASSWORD_HASH)


def create_session_token(username: str) -> str:
    """Issue a signed JWT for the admin session."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    payload = {"sub": username, "exp": expire, "role": "admin"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_session_token(token: str) -> dict | None:
    """Decode/verify a session JWT, returning its claims or ``None``."""
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except JWTError:
        return None


def current_admin(request: Request) -> str | None:
    """Return the logged-in admin username from the session cookie, if valid."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    claims = decode_session_token(token)
    if not claims:
        return None
    return claims.get("sub")
