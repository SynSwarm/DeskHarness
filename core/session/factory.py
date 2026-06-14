"""Session store factory."""

from __future__ import annotations

from app.settings import EngineSettings
from core.session.protocol import SessionStoreProtocol
from core.session_store import SessionStore


def build_session_store(settings: EngineSettings) -> SessionStoreProtocol:
    if settings.session_backend == "redis":
        try:
            from core.session.redis_store import RedisSessionStore
        except ImportError as exc:
            msg = "redis session backend requires: pip install 'deskharness[redis]'"
            raise RuntimeError(msg) from exc
        return RedisSessionStore(
            settings.session_redis_url,
            ttl_seconds=settings.session_ttl_seconds,
        )
    return SessionStore(settings.session_store_path)
