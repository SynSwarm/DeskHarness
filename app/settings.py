"""Engine settings loaded from configs/*.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

InvokeMode = Literal["stub", "turn"]
BrainAdapter = Literal["mock", "http", "prompt-template"]


@dataclass(frozen=True)
class EngineSettings:
    host: str = "127.0.0.1"
    port: int = 8080
    openharness_path_prefix: str = "/openharness"
    openharness_invoke_mode: InvokeMode = "turn"
    dev_mode: bool = True
    session_store_path: Path = Path("memory/sessions/deskharness.db")
    plugin_dirs: tuple[Path, ...] = (Path("plugins"),)
    routes_file: Path = Path("configs/routes.yaml")
    brain_adapter: BrainAdapter = "mock"
    brain_endpoint: str = "http://127.0.0.1:8090/brain"
    brain_timeout_ms: int = 30_000
    brain_template_file: Path = Path("configs/brain.prompt-template.yaml")
    routing_allowed_plugins: tuple[str, ...] = ("order-lookup", "noop", "echo")


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
    brain = raw.get("brain") if isinstance(raw.get("brain"), dict) else {}
    routing = raw.get("routing") if isinstance(raw.get("routing"), dict) else {}

    prefix = str(oh.get("path_prefix") or "/openharness").rstrip("/") or "/openharness"
    if not prefix.startswith("/"):
        prefix = f"/{prefix}"

    invoke_mode_raw = str(oh.get("invoke_mode") or "turn").strip().lower()
    invoke_mode: InvokeMode = "stub" if invoke_mode_raw == "stub" else "turn"

    store_path = Path(str(session.get("store_path") or "memory/sessions/deskharness.db"))
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

    return EngineSettings(
        host=str(listen.get("host") or "127.0.0.1"),
        port=int(listen.get("port") or 8080),
        openharness_path_prefix=prefix,
        openharness_invoke_mode=invoke_mode,
        dev_mode=bool(engine.get("dev_mode", True)),
        session_store_path=store_path,
        plugin_dirs=plugin_dirs,
        routes_file=routes_file,
        brain_adapter=brain_adapter,
        brain_endpoint=str(brain.get("endpoint") or "http://127.0.0.1:8090/brain"),
        brain_timeout_ms=int(brain.get("timeout_ms") or 30_000),
        brain_template_file=template_file,
        routing_allowed_plugins=allowed_plugins,
    )
