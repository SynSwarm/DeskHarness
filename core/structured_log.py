"""JSONL structured turn logs."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class StructuredLogger:
    def __init__(self, log_dir: Path, *, enabled: bool = True) -> None:
        self._enabled = enabled
        self._path = log_dir / "turns.jsonl"
        if enabled:
            log_dir.mkdir(parents=True, exist_ok=True)

    def log_event(self, event: str, payload: dict[str, Any]) -> None:
        if not self._enabled:
            return
        record = {
            "ts": datetime.now(UTC).isoformat(),
            "event": event,
            **payload,
        }
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def log_turn_completed(
        self,
        *,
        trace_id: str,
        turn_id: str,
        session_id: str,
        intent: str,
        plugin_ids: list[str],
        reply: str,
    ) -> None:
        self.log_event(
            "turn.completed",
            {
                "trace_id": trace_id,
                "turn_id": turn_id,
                "session_id": session_id,
                "intent": intent,
                "plugin_ids": plugin_ids,
                "reply_preview": reply[:200],
            },
        )
