"""In-process Engine counters (Phase 3 minimal metrics)."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock


@dataclass
class EngineMetrics:
    turns_total: int = 0
    plugin_dispatches_total: int = 0
    brain_errors_total: int = 0
    rate_limited_total: int = 0
    _lock: Lock = field(default_factory=Lock, repr=False)

    def inc_turn(self) -> None:
        with self._lock:
            self.turns_total += 1

    def inc_plugin_dispatch(self) -> None:
        with self._lock:
            self.plugin_dispatches_total += 1

    def inc_brain_error(self) -> None:
        with self._lock:
            self.brain_errors_total += 1

    def inc_rate_limited(self) -> None:
        with self._lock:
            self.rate_limited_total += 1

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return {
                "turns_total": self.turns_total,
                "plugin_dispatches_total": self.plugin_dispatches_total,
                "brain_errors_total": self.brain_errors_total,
                "rate_limited_total": self.rate_limited_total,
            }

    def prometheus_text(self) -> str:
        snap = self.snapshot()
        lines = [
            "# HELP deskharness_turns_total Completed turns",
            "# TYPE deskharness_turns_total counter",
            f"deskharness_turns_total {snap['turns_total']}",
            "# HELP deskharness_plugin_dispatches_total Plugin dispatches",
            "# TYPE deskharness_plugin_dispatches_total counter",
            f"deskharness_plugin_dispatches_total {snap['plugin_dispatches_total']}",
            "# HELP deskharness_brain_errors_total Brain call failures",
            "# TYPE deskharness_brain_errors_total counter",
            f"deskharness_brain_errors_total {snap['brain_errors_total']}",
            "# HELP deskharness_rate_limited_total Rate-limited requests",
            "# TYPE deskharness_rate_limited_total counter",
            f"deskharness_rate_limited_total {snap['rate_limited_total']}",
        ]
        return "\n".join(lines) + "\n"
