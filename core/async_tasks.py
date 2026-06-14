"""In-memory async plugin callback tasks."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from app.schemas.plugin import PluginResult


@dataclass
class AsyncTaskRecord:
    task_id: str
    plugin_id: str
    command: str
    trace_id: str
    status: str = "pending"
    result: dict[str, Any] | None = None


class AsyncTaskStore:
    def __init__(self) -> None:
        self._tasks: dict[str, AsyncTaskRecord] = {}
        self._lock = threading.Lock()

    def create(self, *, plugin_id: str, command: str, trace_id: str) -> AsyncTaskRecord:
        task_id = f"task_{uuid4().hex[:12]}"
        record = AsyncTaskRecord(
            task_id=task_id,
            plugin_id=plugin_id,
            command=command,
            trace_id=trace_id,
        )
        with self._lock:
            self._tasks[task_id] = record
        return record

    def complete(self, task_id: str, result: PluginResult) -> AsyncTaskRecord | None:
        with self._lock:
            record = self._tasks.get(task_id)
            if record is None:
                return None
            record.status = "completed"
            record.result = result.model_dump(mode="json")
            return record

    def get(self, task_id: str) -> AsyncTaskRecord | None:
        with self._lock:
            return self._tasks.get(task_id)

    def pending_count(self) -> int:
        with self._lock:
            return sum(1 for item in self._tasks.values() if item.status == "pending")
