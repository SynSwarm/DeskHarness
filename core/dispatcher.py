"""Plugin dispatch: local-script, sync-http, async-webhook."""

from __future__ import annotations

import httpx

from app.schemas.plugin import PluginCommand, PluginResult, Verification
from core.async_tasks import AsyncTaskStore
from core.metrics import EngineMetrics
from core.plugin_loader import LoadedPlugin, PluginRegistry
from core.plugin_sandbox import run_handler_subprocess, run_handler_with_timeout
from pkg.plugin.handler import HandlerContext


class PluginDispatcher:
    def __init__(
        self,
        registry: PluginRegistry,
        *,
        allowed_plugins: set[str] | None = None,
        metrics: EngineMetrics | None = None,
        async_tasks: AsyncTaskStore | None = None,
        callback_public_base: str = "http://127.0.0.1:8080",
    ) -> None:
        self._registry = registry
        self._allowed = allowed_plugins
        self._metrics = metrics
        self._async_tasks = async_tasks or AsyncTaskStore()
        self._callback_public_base = callback_public_base.rstrip("/")

    @property
    def async_tasks(self) -> AsyncTaskStore:
        return self._async_tasks

    def dispatch(self, command: PluginCommand) -> PluginResult:
        if self._metrics:
            self._metrics.inc_plugin_dispatch()

        if self._allowed and command.plugin_id not in self._allowed:
            return self._failure(command, f"plugin not allowed: {command.plugin_id}")

        loaded = self._registry.get_plugin(command.plugin_id)
        if loaded is None:
            return self._failure(command, f"plugin not loaded: {command.plugin_id}")

        mode = loaded.manifest.execution_mode
        if mode == "sync-http":
            return self._dispatch_sync_http(loaded, command)
        if mode == "async-webhook":
            return self._dispatch_async_webhook(loaded, command)

        handler = loaded.handlers.get(command.command)
        if handler is None:
            return self._failure(command, f"unknown command: {command.command}")

        ctx = HandlerContext(
            trace_id=command.trace_id,
            turn_id=command.turn_id,
            plugin_id=command.plugin_id,
            command=command.command,
            params=dict(command.params),
            session_vars=dict(command.session_vars),
        )
        execution = loaded.manifest.execution
        timeout_ms = execution.timeout_ms if execution else 5000
        use_sandbox = bool(execution and execution.sandbox)

        if use_sandbox:
            result = run_handler_subprocess(loaded.root, command.command, ctx, timeout_ms=timeout_ms)
        else:
            result = run_handler_with_timeout(handler, ctx, timeout_ms=timeout_ms)

        return PluginResult.model_validate(result.to_plugin_result_dict(command.trace_id))

    def _dispatch_sync_http(self, loaded: LoadedPlugin, command: PluginCommand) -> PluginResult:
        execution = loaded.manifest.execution
        base = (execution.endpoint if execution and execution.endpoint else "").rstrip("/")
        if not base:
            base = f"http://127.0.0.1:8091/plugins/{command.plugin_id}"
        url = f"{base}/{command.command}"
        timeout = (execution.timeout_ms / 1000.0) if execution else 5.0
        payload = command.model_dump(mode="json")

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                return PluginResult.model_validate(response.json())
        except Exception as exc:
            return PluginResult(
                trace_id=command.trace_id,
                status="failure",
                verification=Verification(
                    passed=False,
                    evidence={
                        "plugin_id": command.plugin_id,
                        "command": command.command,
                        "url": url,
                    },
                    failure_reason=str(exc),
                ),
            )

    def _dispatch_async_webhook(self, loaded: LoadedPlugin, command: PluginCommand) -> PluginResult:
        execution = loaded.manifest.execution
        base = (execution.endpoint if execution and execution.endpoint else "").rstrip("/")
        if not base:
            return self._failure(command, "async-webhook requires execution.endpoint")

        record = self._async_tasks.create(
            plugin_id=command.plugin_id,
            command=command.command,
            trace_id=command.trace_id,
        )
        callback_url = f"{self._callback_public_base}/plugins/callbacks/{record.task_id}"
        payload = command.model_dump(mode="json")
        payload["callback_url"] = callback_url
        url = f"{base}/{command.command}"
        timeout = (execution.timeout_ms / 1000.0) if execution else 5.0

        try:
            with httpx.Client(timeout=timeout) as client:
                client.post(url, json=payload)
        except Exception as exc:
            return self._failure(command, f"async-webhook submit failed: {exc}")

        return PluginResult(
            trace_id=command.trace_id,
            status="partial",
            verification=Verification(
                passed=False,
                evidence={
                    "plugin_id": command.plugin_id,
                    "command": command.command,
                    "task_id": record.task_id,
                    "callback_url": callback_url,
                    "async": True,
                },
                failure_reason=None,
            ),
            reply_override={"type": "text", "text": "任务已提交，请稍后查询结果。"},
        )

    @staticmethod
    def _failure(command: PluginCommand, reason: str) -> PluginResult:
        return PluginResult(
            trace_id=command.trace_id,
            status="failure",
            verification=Verification(
                passed=False,
                evidence={"plugin_id": command.plugin_id, "command": command.command},
                failure_reason=reason,
            ),
        )
