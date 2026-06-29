"""Protected dashboard route (empty in Phase 1)."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from web.auth import current_admin
from web.templating import templates

router = APIRouter(tags=["dashboard"])


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render the protected dashboard or redirect to login."""
    admin = current_admin(request)
    if admin is None:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request, "dashboard.html", {"admin": admin}
    )
