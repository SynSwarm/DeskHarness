"""Composition Root: assemble FastAPI app."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.openharness import create_openharness_router
from app.api.shells import create_shells_router
from app.services.runtime import build_plugin_registry, build_turn_engine
from app.settings import EngineSettings, load_settings


def create_app(settings: EngineSettings | None = None) -> FastAPI:
    cfg = settings or load_settings()
    prefix = cfg.openharness_path_prefix
    plugin_registry = build_plugin_registry(cfg)
    turn_engine = build_turn_engine(cfg, plugin_registry) if cfg.openharness_invoke_mode == "turn" else None

    app = FastAPI(title="DeskHarness", version="0.1.0")
    app.state.settings = cfg
    app.state.plugin_registry = plugin_registry
    app.state.turn_engine = turn_engine

    invoke_path = f"{prefix}/invoke"
    app.include_router(
        create_openharness_router(
            invoke_path=invoke_path,
            settings=cfg,
            turn_engine=turn_engine,
        ),
        prefix=prefix,
    )

    if turn_engine is not None:
        app.include_router(
            create_shells_router(
                registry=plugin_registry,
                turn_engine=turn_engine,
            ),
            prefix="/shells",
        )

    return app
