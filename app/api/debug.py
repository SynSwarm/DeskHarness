"""Dev-only debug endpoints (localhost + dev_mode)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request

from app.schemas.brain import BrainResponse
from app.settings import EngineSettings
from core.router import Router


def _require_dev_localhost(request: Request, settings: EngineSettings) -> None:
    if not settings.dev_mode:
        raise HTTPException(status_code=404, detail="debug disabled")
    host = (request.client.host if request.client else "") or ""
    if host not in {"127.0.0.1", "::1", "localhost", "testclient"}:
        raise HTTPException(status_code=403, detail="debug localhost only")


def create_debug_router(*, router: Router | None = None) -> APIRouter:
    api = APIRouter(tags=["debug"])

    @api.get("/routes")
    async def debug_routes(request: Request) -> dict[str, Any]:
        settings: EngineSettings = request.app.state.settings
        _require_dev_localhost(request, settings)
        r: Router = router or request.app.state.router
        return r.export_routes()

    @api.post("/dry-run")
    async def debug_dry_run(
        request: Request,
        body: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        settings: EngineSettings = request.app.state.settings
        _require_dev_localhost(request, settings)
        r: Router = router or request.app.state.router
        brain = BrainResponse.model_validate(body)
        return r.dry_run(brain)

    return api
