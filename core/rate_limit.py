"""Simple in-memory rate limiter (token bucket per key)."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class RateLimiter:
    requests_per_minute: int = 60
    _buckets: dict[str, tuple[float, float]] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock, repr=False)

    def allow(self, key: str) -> bool:
        if self.requests_per_minute <= 0:
            return True

        now = time.monotonic()
        refill_rate = self.requests_per_minute / 60.0
        capacity = float(self.requests_per_minute)

        with self._lock:
            tokens, updated = self._buckets.get(key, (capacity, now))
            elapsed = max(0.0, now - updated)
            tokens = min(capacity, tokens + elapsed * refill_rate)
            if tokens < 1.0:
                self._buckets[key] = (tokens, now)
                return False
            self._buckets[key] = (tokens - 1.0, now)
            return True
