"""Plugin dispatch via manifest-loaded handlers."""

from __future__ import annotations

from app.schemas.plugin import PluginCommand, PluginResult, Verification
from core.plugin_loader import PluginRegistry
from pkg.plugin.handler import HandlerContext


class PluginDispatcher:
    def __init__(
        self,
        registry: PluginRegistry,
        *,
        allowed_plugins: set[str] | None = None,
    ) -> None:
        self._registry = registry
        self._allowed = allowed_plugins

    def dispatch(self, command: PluginCommand) -> PluginResult:
        if self._allowed and command.plugin_id not in self._allowed:
            return PluginResult(
                trace_id=command.trace_id,
                status="failure",
                verification=Verification(
                    passed=False,
                    evidence={"plugin_id": command.plugin_id},
                    failure_reason=f"plugin not allowed: {command.plugin_id}",
                ),
            )

        loaded = self._registry.get_plugin(command.plugin_id)
        if loaded is None:
            return PluginResult(
                trace_id=command.trace_id,
                status="failure",
                verification=Verification(
                    passed=False,
                    evidence={"plugin_id": command.plugin_id},
                    failure_reason=f"plugin not loaded: {command.plugin_id}",
                ),
            )

        handler = loaded.handlers.get(command.command)
        if handler is None:
            return PluginResult(
                trace_id=command.trace_id,
                status="failure",
                verification=Verification(
                    passed=False,
                    evidence={
                        "plugin_id": command.plugin_id,
                        "command": command.command,
                    },
                    failure_reason=f"unknown command: {command.command}",
                ),
            )

        ctx = HandlerContext(
            trace_id=command.trace_id,
            turn_id=command.turn_id,
            plugin_id=command.plugin_id,
            command=command.command,
            params=dict(command.params),
            session_vars=dict(command.session_vars),
        )
        result = handler(ctx)
        return PluginResult.model_validate(result.to_plugin_result_dict(command.trace_id))
