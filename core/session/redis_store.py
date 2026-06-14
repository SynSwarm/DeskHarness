"""Redis-backed Session store (optional dependency)."""

from __future__ import annotations

import json
from uuid import uuid4

from app.schemas.session import Session, SessionContext, SessionSubject


class RedisSessionStore:
    def __init__(self, url: str, *, ttl_seconds: int = 604_800) -> None:
        try:
            import redis
        except ImportError as exc:
            msg = "redis package required: pip install 'deskharness[redis]'"
            raise ImportError(msg) from exc
        self._client = redis.from_url(url, decode_responses=True)
        self._ttl = ttl_seconds

    def _key(self, session_id: str) -> str:
        return f"deskharness:session:{session_id}"

    def get(self, session_id: str) -> Session | None:
        raw = self._client.get(self._key(session_id))
        if not raw:
            return None
        return Session.model_validate(json.loads(raw))

    def get_or_create(
        self,
        *,
        session_id: str | None,
        shell_id: str,
        channel_user_id: str,
        display_name: str = "",
    ) -> Session:
        if session_id:
            existing = self.get(session_id)
            if existing is not None:
                return existing

        sid = session_id or f"sess_{uuid4().hex[:12]}"
        session = Session(
            session_id=sid,
            shell_id=shell_id,
            subject=SessionSubject(
                channel_user_id=channel_user_id or sid,
                display_name=display_name,
            ),
            context=SessionContext(),
        )
        self.save(session)
        return session

    def save(self, session: Session) -> None:
        payload = session.model_dump(mode="json")
        self._client.setex(
            self._key(session.session_id),
            self._ttl,
            json.dumps(payload, ensure_ascii=False),
        )
