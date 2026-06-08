"""Runtime wiring for TurnEngine and dependencies."""

from __future__ import annotations

from app.services.brain_factory import build_brain_client
from app.settings import EngineSettings
from core.dispatcher import PluginDispatcher
from core.engine import TurnEngine
from core.plugin_loader import PluginRegistry
from core.router import Router
from core.session_store import SessionStore


def build_plugin_registry(settings: EngineSettings) -> PluginRegistry:
    return PluginRegistry.from_settings(settings)


def build_turn_engine(settings: EngineSettings, registry: PluginRegistry | None = None) -> TurnEngine:
    plugin_registry = registry or build_plugin_registry(settings)
    router = Router.from_file(settings.routes_file)
    allowed = set(settings.routing_allowed_plugins) | router.allowed_plugins | set(plugin_registry.list_plugin_ids())
    brain_client = build_brain_client(settings)

    return TurnEngine(
        session_store=SessionStore(settings.session_store_path),
        brain_client=brain_client,
        router=router,
        dispatcher=PluginDispatcher(plugin_registry, allowed_plugins=allowed),
    )
