"""Discover plugins/<id>/manifest.yaml and load handlers / shell adapters."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

from app.schemas.manifest import PluginManifest
from app.settings import EngineSettings
from pkg.plugin.handler import HandlerContext, HandlerResult
from pkg.plugin.shell import ShellAdapter

HandlerFn = Callable[[HandlerContext], HandlerResult]


@dataclass
class LoadedPlugin:
    manifest: PluginManifest
    root: Path
    handlers: dict[str, HandlerFn] = field(default_factory=dict)


@dataclass
class LoadedShell:
    manifest: PluginManifest
    root: Path
    adapter: ShellAdapter


class PluginRegistry:
    def __init__(
        self,
        *,
        plugin_dirs: tuple[Path, ...],
        allowed_plugins: set[str] | None = None,
    ) -> None:
        self.plugin_dirs = plugin_dirs
        self.allowed_plugins = allowed_plugins
        self.plugins: dict[str, LoadedPlugin] = {}
        self.shells: dict[str, LoadedShell] = {}
        self._load_all()

    @classmethod
    def from_settings(cls, settings: EngineSettings) -> PluginRegistry:
        allowed = set(settings.routing_allowed_plugins)
        return cls(
            plugin_dirs=settings.plugin_dirs,
            allowed_plugins=allowed,
        )

    def get_plugin(self, plugin_id: str) -> LoadedPlugin | None:
        return self.plugins.get(plugin_id)

    def get_shell(self, shell_id: str) -> LoadedShell | None:
        return self.shells.get(shell_id)

    def list_plugin_ids(self) -> list[str]:
        return sorted(self.plugins.keys())

    def list_shell_ids(self) -> list[str]:
        return sorted(self.shells.keys())

    def _load_all(self) -> None:
        seen: set[str] = set()
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.is_dir():
                continue
            for entry in sorted(plugin_dir.iterdir()):
                if not entry.is_dir() or entry.name.startswith("."):
                    continue
                manifest_path = entry / "manifest.yaml"
                if not manifest_path.is_file():
                    continue
                manifest = self._load_manifest(manifest_path)
                if manifest.plugin_id in seen:
                    continue
                seen.add(manifest.plugin_id)

                if manifest.plugin_type == "shell":
                    if not (entry / "adapter.py").is_file():
                        continue
                    adapter = self._load_shell_adapter(entry, manifest)
                    self.shells[manifest.plugin_id] = LoadedShell(
                        manifest=manifest,
                        root=entry,
                        adapter=adapter,
                    )
                    continue

                if self.allowed_plugins and manifest.plugin_id not in self.allowed_plugins:
                    continue

                handlers: dict[str, HandlerFn] = {}
                if manifest.execution_mode in ("sync-http", "async-webhook"):
                    pass
                elif (entry / "handler.py").is_file():
                    handlers = self._load_plugin_handlers(entry, manifest)
                else:
                    continue

                self.plugins[manifest.plugin_id] = LoadedPlugin(
                    manifest=manifest,
                    root=entry,
                    handlers=handlers,
                )

    @staticmethod
    def _load_manifest(path: Path) -> PluginManifest:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            msg = f"invalid manifest yaml: {path}"
            raise ValueError(msg)
        return PluginManifest.model_validate(raw)

    def _load_plugin_handlers(self, root: Path, manifest: PluginManifest) -> dict[str, HandlerFn]:
        module = self._import_module(root, "handler")
        handlers: dict[str, HandlerFn] = {}

        entry = (manifest.entry or "").strip()
        if entry.startswith("handler:"):
            name = entry.removeprefix("handler:").strip()
            fn = getattr(module, name, None)
            if callable(fn):
                command_name = manifest.commands[0].name if len(manifest.commands) == 1 else name
                handlers[command_name] = fn
            return handlers

        for command in manifest.commands:
            fn = getattr(module, command.name, None)
            if callable(fn):
                handlers[command.name] = fn

        if not handlers:
            ping = getattr(module, "ping", None)
            if callable(ping):
                handlers["ping"] = ping

        return handlers

    def _load_shell_adapter(self, root: Path, manifest: PluginManifest) -> ShellAdapter:
        entry = (manifest.entry or "adapter:WebhookShell").strip()
        if not entry.startswith("adapter:"):
            msg = f"shell entry must be adapter:ClassName, got {entry!r} for {manifest.plugin_id}"
            raise ValueError(msg)

        class_name = entry.removeprefix("adapter:").strip()
        module = self._import_module(root, "adapter")
        adapter_cls = getattr(module, class_name, None)
        if adapter_cls is None:
            msg = f"shell adapter class not found: {class_name} in {root / 'adapter.py'}"
            raise ValueError(msg)
        adapter = adapter_cls()
        if not hasattr(adapter, "to_invoke_request") or not hasattr(adapter, "from_invoke_response"):
            msg = f"{class_name} does not implement ShellAdapter protocol"
            raise ValueError(msg)
        return adapter

    @staticmethod
    def _import_module(root: Path, module_name: str) -> Any:
        file_path = root / f"{module_name}.py"
        if not file_path.is_file():
            msg = f"missing {module_name}.py under {root}"
            raise ValueError(msg)

        qualified = f"deskharness_plugin_{root.name}_{module_name}"
        spec = importlib.util.spec_from_file_location(qualified, file_path)
        if spec is None or spec.loader is None:
            msg = f"cannot import {file_path}"
            raise ValueError(msg)

        module = importlib.util.module_from_spec(spec)
        sys.modules[qualified] = module
        spec.loader.exec_module(module)
        return module
