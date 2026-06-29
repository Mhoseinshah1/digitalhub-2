"""Shared FastAPI dependencies for the web panel."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import RedirectResponse

from web.auth import current_admin


class RequireLogin(Exception):
    """Raised to signal that a login redirect is needed."""


def require_admin(request: Request) -> str:
    """Dependency that returns the admin username or raises a redirect.

    Routers using this should let the exception handler turn it into a
    redirect to the login page.
    """
    username = current_admin(request)
    if username is None:
        raise RequireLogin()
    return username


def login_redirect() -> RedirectResponse:
    """Build a redirect response to the login page."""
    return RedirectResponse(url="/login", status_code=303)
