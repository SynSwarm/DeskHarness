"""Composition Root: assemble FastAPI app."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.callbacks import create_callbacks_router
from app.api.debug import create_debug_router
from app.api.metrics import create_metrics_router
from app.api.openharness import create_openharness_router
from app.api.shells import create_shells_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.services.runtime import build_plugin_registry, build_turn_engine
from app.settings import EngineSettings, load_settings
from core.async_tasks import AsyncTaskStore
from core.metrics import EngineMetrics
from core.rate_limit import RateLimiter
from core.router import Router


def create_app(settings: EngineSettings | None = None) -> FastAPI:
    cfg = settings or load_settings()
    prefix = cfg.openharness_path_prefix
    plugin_registry = build_plugin_registry(cfg)
    metrics = EngineMetrics()
    async_tasks = AsyncTaskStore()
    turn_engine = (
        build_turn_engine(cfg, plugin_registry, metrics=metrics, async_tasks=async_tasks)
        if cfg.openharness_invoke_mode == "turn"
        else None
    )
    router = Router.from_file(cfg.routes_file)

    app = FastAPI(title="DeskHarness", version="0.1.0")
    app.state.settings = cfg
    app.state.plugin_registry = plugin_registry
    app.state.turn_engine = turn_engine
    app.state.metrics = metrics
    app.state.async_tasks = async_tasks
    app.state.router = router

    if cfg.rate_limit_enabled:
        limiter = RateLimiter(requests_per_minute=cfg.rate_limit_requests_per_minute)
        app.add_middleware(RateLimitMiddleware, limiter=limiter, settings=cfg, metrics=metrics)

    invoke_path = f"{prefix}/invoke"
    app.include_router(
        create_openharness_router(
            invoke_path=invoke_path,
            settings=cfg,
            turn_engine=turn_engine,
        ),
        prefix=prefix,
    )
    app.include_router(create_metrics_router(metrics=metrics))

    if turn_engine is not None:
        app.include_router(
            create_shells_router(
                registry=plugin_registry,
                turn_engine=turn_engine,
            ),
            prefix="/shells",
        )
        app.include_router(create_callbacks_router(async_tasks=async_tasks))

    if cfg.dev_mode:
        app.include_router(create_debug_router(router=router), prefix="/debug")

    return app
