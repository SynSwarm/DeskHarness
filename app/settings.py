"""Engine settings loaded from configs/*.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

InvokeMode = Literal["stub", "turn"]
BrainAdapter = Literal["mock", "http", "prompt-template"]
SessionBackend = Literal["embedded_sqlite", "redis"]


@dataclass(frozen=True)
class EngineSettings:
    host: str = "127.0.0.1"
    port: int = 8080
    openharness_path_prefix: str = "/openharness"
    openharness_invoke_mode: InvokeMode = "turn"
    dev_mode: bool = True
    session_backend: SessionBackend = "embedded_sqlite"
    session_store_path: Path = Path("memory/sessions/deskharness.db")
    session_redis_url: str = "redis://127.0.0.1:6379/0"
    session_ttl_seconds: int = 604_800
    log_dir: Path = Path("memory/logs")
    log_enabled: bool = True
    plugin_dirs: tuple[Path, ...] = (Path("plugins"),)
    routes_file: Path = Path("configs/routes.yaml")
    brain_adapter: BrainAdapter = "mock"
    brain_endpoint: str = "http://127.0.0.1:8090/brain"
    brain_timeout_ms: int = 30_000
    brain_template_file: Path = Path("configs/brain.prompt-template.yaml")
    routing_allowed_plugins: tuple[str, ...] = ("order-lookup", "noop", "echo")
    rate_limit_enabled: bool = False
    rate_limit_requests_per_minute: int = 60
    context_max_turns: int = 20
    context_keep_recent: int = 10
    callback_public_base: str = "http://127.0.0.1:8080"


def load_settings(config_path: str | Path = "configs/config.yaml") -> EngineSettings:
    path = Path(config_path)
    if not path.is_file():
        path = Path("configs/config.template.yaml")

    raw: dict[str, Any] = {}
    if path.is_file():
        with path.open(encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh) or {}
            if isinstance(loaded, dict):
                raw = loaded

    engine = raw.get("engine") if isinstance(raw.get("engine"), dict) else {}
    listen = engine.get("listen") if isinstance(engine.get("listen"), dict) else {}
    oh = engine.get("openharness") if isinstance(engine.get("openharness"), dict) else {}
    session = engine.get("session") if isinstance(engine.get("session"), dict) else {}
    rate_limit = engine.get("rate_limit") if isinstance(engine.get("rate_limit"), dict) else {}
    context_cfg = engine.get("context") if isinstance(engine.get("context"), dict) else {}
    brain = raw.get("brain") if isinstance(raw.get("brain"), dict) else {}
    routing = raw.get("routing") if isinstance(raw.get("routing"), dict) else {}
    logging_cfg = raw.get("logging") if isinstance(raw.get("logging"), dict) else {}

    prefix = str(oh.get("path_prefix") or "/openharness").rstrip("/") or "/openharness"
    if not prefix.startswith("/"):
        prefix = f"/{prefix}"

    invoke_mode_raw = str(oh.get("invoke_mode") or "turn").strip().lower()
    invoke_mode: InvokeMode = "stub" if invoke_mode_raw == "stub" else "turn"

    store_path = Path(str(session.get("store_path") or "memory/sessions/deskharness.db"))
    backend_raw = str(session.get("backend") or "embedded_sqlite").strip().lower()
    session_backend: SessionBackend = "redis" if backend_raw == "redis" else "embedded_sqlite"
    redis_url = str(session.get("redis_url") or "redis://127.0.0.1:6379/0")
    ttl_hours = int(session.get("ttl_hours") or 168)
    log_dir = Path(str(logging_cfg.get("path") or "memory/logs"))
    log_enabled = str(logging_cfg.get("level") or "info").lower() != "off"
    plugin_dirs_raw = engine.get("plugin_dirs") or ["./plugins"]
    plugin_dirs = tuple(
        Path(str(item)) for item in plugin_dirs_raw if isinstance(item, (str, Path))
    ) or (Path("plugins"),)

    routes_file = Path(str(routing.get("routes_file") or "configs/routes.yaml"))
    allowed_raw = routing.get("allowed_plugins") or ["order-lookup", "noop", "echo"]
    allowed_plugins = tuple(str(item) for item in allowed_raw)

    adapter_raw = str(brain.get("adapter") or "mock").strip().lower()
    if adapter_raw == "http":
        brain_adapter: BrainAdapter = "http"
    elif adapter_raw in ("prompt-template", "prompt_template", "template"):
        brain_adapter = "prompt-template"
    else:
        brain_adapter = "mock"

    template_file = Path(
        str(brain.get("template_file") or "configs/brain.prompt-template.yaml")
    )

    listen_host = str(listen.get("host") or "127.0.0.1")
    listen_port = int(listen.get("port") or 8080)
    callback_base = str(
        engine.get("callback_public_base") or f"http://{listen_host}:{listen_port}"
    )

    return EngineSettings(
        host=listen_host,
        port=listen_port,
        openharness_path_prefix=prefix,
        openharness_invoke_mode=invoke_mode,
        dev_mode=bool(engine.get("dev_mode", True)),
        session_backend=session_backend,
        session_store_path=store_path,
        session_redis_url=redis_url,
        session_ttl_seconds=ttl_hours * 3600,
        log_dir=log_dir,
        log_enabled=log_enabled,
        plugin_dirs=plugin_dirs,
        routes_file=routes_file,
        brain_adapter=brain_adapter,
        brain_endpoint=str(brain.get("endpoint") or "http://127.0.0.1:8090/brain"),
        brain_timeout_ms=int(brain.get("timeout_ms") or 30_000),
        brain_template_file=template_file,
        routing_allowed_plugins=allowed_plugins,
        rate_limit_enabled=bool(rate_limit.get("enabled", False)),
        rate_limit_requests_per_minute=int(rate_limit.get("requests_per_minute") or 60),
        context_max_turns=int(context_cfg.get("max_turns") or session.get("max_turns") or 20),
        context_keep_recent=int(context_cfg.get("keep_recent") or session.get("keep_recent") or 10),
        callback_public_base=callback_base,
    )
