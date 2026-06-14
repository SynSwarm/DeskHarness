"""Session store protocol."""

from __future__ import annotations

from typing import Protocol

from app.schemas.session import Session


class SessionStoreProtocol(Protocol):
    def get(self, session_id: str) -> Session | None: ...

    def get_or_create(
        self,
        *,
        session_id: str | None,
        shell_id: str,
        channel_user_id: str,
        display_name: str = "",
    ) -> Session: ...

    def save(self, session: Session) -> None: ...
