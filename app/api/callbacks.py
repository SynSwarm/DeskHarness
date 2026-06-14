"""Async plugin callback endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.schemas.plugin import PluginResult
from core.async_tasks import AsyncTaskStore


def create_callbacks_router(*, async_tasks: AsyncTaskStore) -> APIRouter:
    router = APIRouter(tags=["callbacks"])

    @router.get("/plugins/callbacks/{task_id}")
    def get_callback_task(task_id: str) -> dict:
        record = async_tasks.get(task_id)
        if record is None:
            raise HTTPException(status_code=404, detail="task not found")
        return {
            "task_id": record.task_id,
            "plugin_id": record.plugin_id,
            "command": record.command,
            "trace_id": record.trace_id,
            "status": record.status,
            "result": record.result,
        }

    @router.post("/plugins/callbacks/{task_id}")
    async def complete_callback_task(task_id: str, request: Request) -> dict:
        body = await request.json()
        result = PluginResult.model_validate(body)
        record = async_tasks.complete(task_id, result)
        if record is None:
            raise HTTPException(status_code=404, detail="task not found")
        return {
            "task_id": record.task_id,
            "status": record.status,
        }

    return router
