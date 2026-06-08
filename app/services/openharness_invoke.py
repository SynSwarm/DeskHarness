"""OpenHarness invoke mapping (Phase 1 stub + turn engine)."""

from __future__ import annotations

import os
from typing import Any, Literal

from app.schemas.openharness import (
    SUPPORTED_PROTOCOL_VERSIONS,
    OpenHarnessActionDirective,
    OpenHarnessErrorBody,
    OpenHarnessInvokeErrorResponse,
    OpenHarnessInvokeRequest,
    OpenHarnessInvokeResponse,
    OpenHarnessResponsePayload,
)
from app.settings import EngineSettings
from core.engine import TurnEngine

StubMode = Literal["minimal_200", "not_implemented_501"]

STUB_MODE_ENV = "DH_OPENHARNESS_STUB_MODE"


def _env_stub_mode() -> StubMode | None:
    raw = (os.environ.get(STUB_MODE_ENV) or "").strip().lower()
    if not raw:
        return None
    if raw in ("501", "not_implemented", "not_implemented_501"):
        return "not_implemented_501"
    if raw in ("minimal_200", "stub", "minimal"):
        return "minimal_200"
    return None


def invoke_openharness(
    body: dict[str, Any],
    *,
    settings: EngineSettings | None = None,
    turn_engine: TurnEngine | None = None,
) -> tuple[OpenHarnessInvokeResponse | OpenHarnessInvokeErrorResponse, int]:
    env_mode = _env_stub_mode()
    if env_mode == "not_implemented_501":
        return _stub_not_implemented(body), 501
    if env_mode == "minimal_200":
        return invoke_openharness_stub(body)

    cfg = settings
    if cfg is not None and cfg.openharness_invoke_mode == "stub":
        return invoke_openharness_stub(body)

    if turn_engine is not None:
        return turn_engine.process(body)

    return invoke_openharness_stub(body)


def invoke_openharness_stub(
    body: dict[str, Any],
) -> tuple[OpenHarnessInvokeResponse | OpenHarnessInvokeErrorResponse, int]:
    req = OpenHarnessInvokeRequest.model_validate(body)
    if req.protocol_version not in SUPPORTED_PROTOCOL_VERSIONS:
        return build_protocol_version_error(req), 200
    return build_stub_success(req), 200


def _stub_not_implemented(body: dict[str, Any]) -> OpenHarnessInvokeErrorResponse:
    return OpenHarnessInvokeErrorResponse(
        protocol_version="1.0.0",
        request_id=str(body.get("request_id") or ""),
        supported_protocol_versions=list(SUPPORTED_PROTOCOL_VERSIONS),
        error=OpenHarnessErrorBody(
            code="not_implemented",
            message=f"OpenHarness stub: set {STUB_MODE_ENV}=minimal_200 for success JSON",
            retryable=True,
        ),
    )


def build_stub_success(req: OpenHarnessInvokeRequest) -> OpenHarnessInvokeResponse:
    ctx = req.request.get("context") if isinstance(req.request, dict) else {}
    user_intent = ""
    if isinstance(ctx, dict):
        user_intent = str(ctx.get("user_intent") or "").strip()

    text = user_intent or "Hello, OpenHarness."
    return OpenHarnessInvokeResponse(
        protocol_version="1.0.0",
        request_id=req.request_id or "req_stub",
        supported_protocol_versions=list(SUPPORTED_PROTOCOL_VERSIONS),
        response=OpenHarnessResponsePayload(
            status="success",
            action_directives=[
                OpenHarnessActionDirective(
                    action_type="render_message",
                    payload={"text": text},
                )
            ],
        ),
    )


def build_protocol_version_error(req: OpenHarnessInvokeRequest) -> OpenHarnessInvokeErrorResponse:
    return OpenHarnessInvokeErrorResponse(
        protocol_version="1.0.0",
        request_id=req.request_id or "req_stub",
        supported_protocol_versions=list(SUPPORTED_PROTOCOL_VERSIONS),
        error=OpenHarnessErrorBody(
            code="protocol_version_unsupported",
            message=(
                f"supported: {', '.join(SUPPORTED_PROTOCOL_VERSIONS)}; "
                f"got: {req.protocol_version!r}"
            ),
            retryable=False,
        ),
    )
