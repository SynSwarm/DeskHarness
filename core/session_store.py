"""SQLite-backed Session store."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.schemas.session import Session, SessionContext, SessionSubject


class SessionStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    shell_id TEXT NOT NULL,
                    channel_user_id TEXT NOT NULL,
                    subject_json TEXT NOT NULL,
                    context_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def get(self, session_id: str) -> Session | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_session(row)

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
        now = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    session_id, shell_id, channel_user_id,
                    subject_json, context_json, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    shell_id = excluded.shell_id,
                    channel_user_id = excluded.channel_user_id,
                    subject_json = excluded.subject_json,
                    context_json = excluded.context_json,
                    updated_at = excluded.updated_at
                """,
                (
                    session.session_id,
                    session.shell_id,
                    session.subject.channel_user_id,
                    session.subject.model_dump_json(),
                    session.context.model_dump_json(),
                    now,
                ),
            )

    @staticmethod
    def _row_to_session(row: sqlite3.Row) -> Session:
        subject = SessionSubject.model_validate(json.loads(row["subject_json"]))
        context = SessionContext.model_validate(json.loads(row["context_json"]))
        return Session(
            session_id=row["session_id"],
            shell_id=row["shell_id"],
            subject=subject,
            context=context,
        )
