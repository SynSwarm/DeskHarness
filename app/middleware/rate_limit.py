"""ASGI rate-limit middleware for invoke / shell inbound paths."""

from __future__ import annotations

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.settings import EngineSettings
from core.metrics import EngineMetrics
from core.rate_limit import RateLimiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        *,
        limiter: RateLimiter,
        settings: EngineSettings,
        metrics: EngineMetrics | None = None,
    ) -> None:
        super().__init__(app)
        self._limiter = limiter
        self._settings = settings
        self._metrics = metrics

    async def dispatch(self, request: Request, call_next: Callable):
        if not self._settings.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path
        if not self._should_limit(path):
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown"
        if not self._limiter.allow(client_host):
            if self._metrics:
                self._metrics.inc_rate_limited()
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "rate_limit_exceeded",
                        "message": "Too many requests; try again later.",
                        "retryable": True,
                    }
                },
            )
        return await call_next(request)

    def _should_limit(self, path: str) -> bool:
        prefix = self._settings.openharness_path_prefix.rstrip("/")
        if path == f"{prefix}/invoke" or path.endswith("/invoke"):
            return True
        return path.startswith("/shells/") and path.endswith("/inbound")
