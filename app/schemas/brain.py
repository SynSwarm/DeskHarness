"""Brain wire types (Engine ↔ 大脑引擎)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BrainInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = "text"
    text: str = ""


class BrainContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    recent_turns: list[dict[str, Any]] = Field(default_factory=list)
    session_vars: dict[str, Any] = Field(default_factory=dict)


class BrainRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    request_version: str = "0.2"
    trace_id: str
    turn_id: str
    session_id: str
    input: BrainInput
    context: BrainContext = Field(default_factory=BrainContext)
    available_intents: list[str] = Field(default_factory=list)


class BrainTarget(BaseModel):
    model_config = ConfigDict(extra="allow")

    statement: str = ""
    success_criteria: str | None = None


class BrainReply(BaseModel):
    model_config = ConfigDict(extra="allow")

    type: str = "text"
    text: str = ""


class PlanStep(BaseModel):
    model_config = ConfigDict(extra="allow")

    plugin_id: str
    command: str
    params: dict[str, Any] = Field(default_factory=dict)


class BrainPlan(BaseModel):
    model_config = ConfigDict(extra="allow")

    mode: str = "single"
    steps: list[PlanStep] = Field(default_factory=list)


class BrainDecision(BaseModel):
    model_config = ConfigDict(extra="allow")

    target: BrainTarget | None = None
    intent: str = "general.chat"
    confidence: float = 1.0
    entities: dict[str, Any] = Field(default_factory=dict)
    plan: BrainPlan = Field(default_factory=BrainPlan)
    reply: BrainReply | None = None


class BrainResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    response_version: str = "0.2"
    trace_id: str
    decision: BrainDecision
