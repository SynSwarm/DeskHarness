"""OpenHarness HTTP routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.services.openharness_invoke import invoke_openharness
from app.settings import EngineSettings
from core.engine import TurnEngine


def create_openharness_router(
    *,
    invoke_path: str = "/invoke",
    settings: EngineSettings | None = None,
    turn_engine: TurnEngine | None = None,
) -> APIRouter:
    router = APIRouter(tags=["openharness"])

    @router.get("/health")
    async def openharness_health(request: Request) -> dict[str, Any]:
        cfg: EngineSettings = settings or request.app.state.settings
        return {
            "status": "ok",
            "invoke_mode": cfg.openharness_invoke_mode,
            "stub": cfg.openharness_invoke_mode == "stub",
            "invoke": invoke_path,
        }

    @router.post("/invoke")
    async def openharness_invoke(
        request: Request,
        body: dict[str, Any] = Body(...),
    ) -> JSONResponse:
        cfg: EngineSettings = settings or request.app.state.settings
        engine: TurnEngine | None = turn_engine or getattr(request.app.state, "turn_engine", None)
        try:
            result, status = invoke_openharness(body, settings=cfg, turn_engine=engine)
        except ValidationError as exc:
            return JSONResponse(
                status_code=422,
                content={
                    "detail": exc.errors(),
                    "hint": "see schemas/openharness/fixtures/minimal-request.json",
                },
            )
        return JSONResponse(status_code=status, content=result.model_dump(mode="json"))

    return router
