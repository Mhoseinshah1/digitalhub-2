"""FastAPI application entrypoint for the web admin panel.

Phase 1: a bcrypt-verified login, a JWT session cookie, and an empty
protected dashboard. No CRUD yet.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from web.routers import auth as auth_router
from web.routers import dashboard as dashboard_router

STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(title="AppStore Admin Panel", docs_url=None, redoc_url=None)

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    app.include_router(auth_router.router)
    app.include_router(dashboard_router.router)

    @app.get("/healthz", include_in_schema=False)
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
