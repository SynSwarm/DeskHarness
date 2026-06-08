"""Public plugin SDK types (plugins depend on pkg/ only)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HandlerContext:
    trace_id: str
    turn_id: str
    plugin_id: str
    command: str
    params: dict[str, Any] = field(default_factory=dict)
    session_vars: dict[str, Any] = field(default_factory=dict)


@dataclass
class HandlerResult:
    status: str
    passed: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    failure_reason: str | None = None
    reply_text: str | None = None

    def to_plugin_result_dict(self, trace_id: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "result_version": "0.2",
            "trace_id": trace_id,
            "status": self.status,
            "verification": {
                "passed": self.passed,
                "evidence": self.evidence,
                "failure_reason": self.failure_reason,
            },
            "error": None,
            "reply_override": None,
        }
        if self.reply_text:
            payload["reply_override"] = {"type": "text", "text": self.reply_text}
        return payload


def success(
    ctx: HandlerContext,
    *,
    evidence: dict[str, Any] | None = None,
    reply_text: str | None = None,
) -> HandlerResult:
    merged = {"plugin_id": ctx.plugin_id, "command": ctx.command}
    if evidence:
        merged.update(evidence)
    return HandlerResult(
        status="success",
        passed=True,
        evidence=merged,
        reply_text=reply_text,
    )


def failure(ctx: HandlerContext, reason: str, *, evidence: dict[str, Any] | None = None) -> HandlerResult:
    merged = {"plugin_id": ctx.plugin_id, "command": ctx.command}
    if evidence:
        merged.update(evidence)
    return HandlerResult(
        status="failure",
        passed=False,
        evidence=merged,
        failure_reason=reason,
    )
