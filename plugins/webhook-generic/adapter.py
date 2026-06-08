"""Generic webhook Shell adapter."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from pkg.plugin.shell import ShellAdapter


class WebhookShell:
    shell_id = "webhook-generic"

    def to_invoke_request(self, raw: dict[str, Any]) -> dict[str, Any]:
        text = str(raw.get("text") or raw.get("message") or raw.get("user_intent") or "").strip()
        session_id = str(raw.get("session_id") or f"sess_{uuid4().hex[:12]}")
        user_id = str(raw.get("user_id") or raw.get("channel_user_id") or f"webhook:{session_id}")

        return {
            "protocol_version": "1.0.0",
            "request_id": str(raw.get("request_id") or f"req_{uuid4().hex[:12]}"),
            "correlation_id": raw.get("correlation_id"),
            "request": {
                "context": {
                    "session_id": session_id,
                    "shell_id": self.shell_id,
                    "channel_user_id": user_id,
                    "user_intent": text,
                }
            },
        }

    def from_invoke_response(self, response: dict[str, Any]) -> dict[str, Any]:
        if "error" in response:
            error = response.get("error") or {}
            return {
                "ok": False,
                "error": {
                    "code": error.get("code"),
                    "message": error.get("message"),
                },
                "raw": response,
            }

        directives = (response.get("response") or {}).get("action_directives") or []
        text = ""
        if directives:
            payload = directives[0].get("payload") or {}
            text = str(payload.get("text") or "")

        return {
            "ok": True,
            "reply": text,
            "request_id": response.get("request_id"),
            "raw": response,
        }
