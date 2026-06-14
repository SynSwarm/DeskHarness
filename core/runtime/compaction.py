"""Compact long session context before Brain calls."""

from __future__ import annotations

from app.schemas.session import Session


def compact_session_context(
    session: Session,
    *,
    max_turns: int = 20,
    keep_recent: int = 10,
) -> None:
    turns = session.recent_turns
    if len(turns) <= max_turns:
        return

    keep = max(1, min(keep_recent, max_turns))
    old_turns = turns[:-keep]
    summary_parts: list[str] = []
    for turn in old_turns:
        user_input = str(turn.get("input") or "").strip()
        reply = str(turn.get("reply") or "").strip()
        if user_input or reply:
            summary_parts.append(f"{user_input} -> {reply}")

    if summary_parts:
        prior = str(session.session_vars.get("_context_summary") or "").strip()
        merged = "; ".join([prior, *summary_parts]) if prior else "; ".join(summary_parts)
        session.session_vars["_context_summary"] = merged[:4000]

    session.recent_turns[:] = turns[-keep:]
