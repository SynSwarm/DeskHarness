"""Shell inbound HTTP routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import JSONResponse

from core.engine import TurnEngine
from core.plugin_loader import PluginRegistry


def create_shells_router(
    *,
    path_prefix: str = "/shells",
    registry: PluginRegistry | None = None,
    turn_engine: TurnEngine | None = None,
) -> APIRouter:
    router = APIRouter(tags=["shells"])

    @router.get("")
    async def list_shells(request: Request) -> dict[str, Any]:
        reg: PluginRegistry = registry or request.app.state.plugin_registry
        return {"shells": reg.list_shell_ids()}

    @router.post("/webhook-generic/inbound")
    async def webhook_generic_inbound(
        request: Request,
        body: dict[str, Any] = Body(...),
    ) -> JSONResponse:
        reg: PluginRegistry = registry or request.app.state.plugin_registry
        engine: TurnEngine = turn_engine or request.app.state.turn_engine
        loaded = reg.get_shell("webhook-generic")
        if loaded is None:
            raise HTTPException(status_code=503, detail="webhook-generic shell not loaded")

        oh_body = loaded.adapter.to_invoke_request(body)
        result, status = engine.process(oh_body)
        outbound = loaded.adapter.from_invoke_response(result.model_dump(mode="json"))
        return JSONResponse(status_code=status, content=outbound)

    return router
