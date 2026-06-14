"""Metrics endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse

from core.metrics import EngineMetrics


def create_metrics_router(*, metrics: EngineMetrics | None = None) -> APIRouter:
    router = APIRouter(tags=["metrics"])

    @router.get("/metrics")
    async def prometheus_metrics(request: Request) -> PlainTextResponse:
        m: EngineMetrics = metrics or request.app.state.metrics
        return PlainTextResponse(m.prometheus_text(), media_type="text/plain; version=0.0.4")

    @router.get("/metrics/json")
    async def json_metrics(request: Request) -> dict:
        m: EngineMetrics = metrics or request.app.state.metrics
        return m.snapshot()

    return router
