"""Plugin / Shell manifest (plugins/<id>/manifest.yaml)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PluginType = Literal["shell", "plugin"]
ExecutionMode = Literal["local-script", "sync-http", "in-process"]


class CommandSpec(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    target: str = ""


class ExecutionSpec(BaseModel):
    model_config = ConfigDict(extra="allow")

    mode: ExecutionMode = "local-script"
    timeout_ms: int = 5000
    endpoint: str | None = None


class VerificationSpec(BaseModel):
    model_config = ConfigDict(extra="allow")

    mode: str = "self_report"


class ExportSpec(BaseModel):
    model_config = ConfigDict(extra="allow")

    from_: str = Field(alias="from")
    to: str


class CapabilitiesSpec(BaseModel):
    model_config = ConfigDict(extra="allow")

    inbound_types: list[str] = Field(default_factory=list)
    outbound_types: list[str] = Field(default_factory=list)


class PluginManifest(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    plugin_id: str
    plugin_type: PluginType
    version: str = "0.1.0"
    api_version: str = "0.2"
    entry: str | None = None
    execution: ExecutionSpec | None = None
    commands: list[CommandSpec] = Field(default_factory=list)
    verification: VerificationSpec | None = None
    exports: list[ExportSpec] = Field(default_factory=list)
    capabilities: CapabilitiesSpec | None = None

    @property
    def command_names(self) -> set[str]:
        return {cmd.name for cmd in self.commands}

    @property
    def execution_mode(self) -> ExecutionMode:
        if self.execution is None:
            return "local-script"
        return self.execution.mode
