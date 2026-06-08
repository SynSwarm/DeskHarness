"""Session runtime model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SessionSubject(BaseModel):
    model_config = ConfigDict(extra="allow")

    channel_user_id: str = ""
    display_name: str = ""


class SessionContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    recent_turns: list[dict[str, Any]] = Field(default_factory=list)
    session_vars: dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    model_config = ConfigDict(extra="allow")

    session_id: str
    shell_id: str = "webhook-generic"
    subject: SessionSubject = Field(default_factory=SessionSubject)
    context: SessionContext = Field(default_factory=SessionContext)

    @property
    def recent_turns(self) -> list[dict[str, Any]]:
        return self.context.recent_turns

    @property
    def session_vars(self) -> dict[str, Any]:
        return self.context.session_vars
