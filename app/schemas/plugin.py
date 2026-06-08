"""Plugin wire types (Engine ↔ 插件)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PluginCommand(BaseModel):
    model_config = ConfigDict(extra="allow")

    command_version: str = "0.2"
    trace_id: str
    turn_id: str
    plugin_id: str
    command: str
    params: dict[str, Any] = Field(default_factory=dict)
    session_vars: dict[str, Any] = Field(default_factory=dict)


class VerificationCheck(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str = ""
    passed: bool = True


class Verification(BaseModel):
    model_config = ConfigDict(extra="allow")

    passed: bool
    evidence: dict[str, Any] = Field(default_factory=dict)
    checks: list[VerificationCheck] = Field(default_factory=list)
    failure_reason: str | None = None


class PluginResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    result_version: str = "0.2"
    trace_id: str
    status: str
    verification: Verification
    error: dict[str, Any] | None = None
    reply_override: dict[str, Any] | None = None
