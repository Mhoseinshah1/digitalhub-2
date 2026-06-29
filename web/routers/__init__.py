"""FastAPI routers."""

from web.routers import auth as auth_router
from web.routers import dashboard as dashboard_router

__all__ = ["auth_router", "dashboard_router"]
