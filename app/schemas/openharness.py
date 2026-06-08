"""OpenHarness wire types (MVP subset aligned with schemas/openharness/*.json)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

SUPPORTED_PROTOCOL_VERSIONS: tuple[str, ...] = ("1.0.0",)


class OpenHarnessErrorBody(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: str
    message: str
    retryable: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class OpenHarnessActionDirective(BaseModel):
    model_config = ConfigDict(extra="allow")

    action_type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class OpenHarnessResponsePayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    status: str = "success"
    action_directives: list[OpenHarnessActionDirective] = Field(default_factory=list)


class OpenHarnessInvokeResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    protocol_version: str = "1.0.0"
    request_id: str = ""
    supported_protocol_versions: list[str] = Field(
        default_factory=lambda: list(SUPPORTED_PROTOCOL_VERSIONS)
    )
    response: OpenHarnessResponsePayload = Field(default_factory=OpenHarnessResponsePayload)


class OpenHarnessInvokeErrorResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    protocol_version: str = "1.0.0"
    request_id: str = ""
    supported_protocol_versions: list[str] = Field(
        default_factory=lambda: list(SUPPORTED_PROTOCOL_VERSIONS)
    )
    error: OpenHarnessErrorBody


class OpenHarnessInvokeRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    protocol_version: str = "1.0.0"
    request_id: str = ""
    correlation_id: str | None = None
    request: dict[str, Any] = Field(default_factory=dict)
