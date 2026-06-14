"""Runtime wiring for TurnEngine and dependencies."""

from __future__ import annotations

from app.services.brain_factory import build_brain_client
from app.settings import EngineSettings
from core.async_tasks import AsyncTaskStore
from core.dispatcher import PluginDispatcher
from core.engine import TurnEngine
from core.metrics import EngineMetrics
from core.plugin_loader import PluginRegistry
from core.router import Router
from core.session.factory import build_session_store
from core.structured_log import StructuredLogger


def build_plugin_registry(settings: EngineSettings) -> PluginRegistry:
    return PluginRegistry.from_settings(settings)


def build_turn_engine(
    settings: EngineSettings,
    registry: PluginRegistry | None = None,
    *,
    metrics: EngineMetrics | None = None,
    logger: StructuredLogger | None = None,
    async_tasks: AsyncTaskStore | None = None,
) -> TurnEngine:
    plugin_registry = registry or build_plugin_registry(settings)
    router = Router.from_file(settings.routes_file)
    allowed = set(settings.routing_allowed_plugins) | router.allowed_plugins | set(plugin_registry.list_plugin_ids())
    brain_client = build_brain_client(settings)
    m = metrics or EngineMetrics()
    log = logger or StructuredLogger(settings.log_dir, enabled=settings.log_enabled)
    tasks = async_tasks or AsyncTaskStore()

    dispatcher = PluginDispatcher(
        plugin_registry,
        allowed_plugins=allowed,
        metrics=m,
        async_tasks=tasks,
        callback_public_base=settings.callback_public_base,
    )

    engine = TurnEngine(
        session_store=build_session_store(settings),
        brain_client=brain_client,
        router=router,
        dispatcher=dispatcher,
        logger=log,
        metrics=m,
        context_max_turns=settings.context_max_turns,
        context_keep_recent=settings.context_keep_recent,
    )
    return engine
