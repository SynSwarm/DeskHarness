"""routes.yaml R 层求值（Phase 1 子集）."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app.schemas.brain import BrainDecision, BrainResponse, PlanStep
from app.schemas.plugin import PluginResult, Verification


@dataclass(frozen=True)
class RouteOutcome:
    plugin_id: str | None = None
    command: str | None = None
    params: dict[str, Any] | None = None
    reply_text: str | None = None
    require_confirmation: bool = False


class Router:
    def __init__(self, routes_config: dict[str, Any]) -> None:
        self._config = routes_config
        self._routes: list[dict[str, Any]] = list(routes_config.get("routes") or [])
        self._fallback: dict[str, Any] = dict(routes_config.get("fallback") or {})
        self._routing: dict[str, Any] = dict(routes_config.get("routing") or {})

    @classmethod
    def from_file(cls, path: Path) -> Router:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            raw = {}
        return cls(raw)

    @property
    def mode(self) -> str:
        return str(self._routing.get("mode") or "brain_led")

    @property
    def allowed_plugins(self) -> set[str]:
        return set(self._routing.get("allowed_plugins") or [])

    def available_intents(self) -> list[str]:
        descriptions = self._routing.get("intent_descriptions") or {}
        if isinstance(descriptions, dict):
            return list(descriptions.keys())
        return []

    def intent_descriptions(self) -> dict[str, str]:
        raw = self._routing.get("intent_descriptions") or {}
        return dict(raw) if isinstance(raw, dict) else {}

    def brain_fallback_reply(self, *, on_timeout: bool = False) -> str:
        key = "on_brain_timeout" if on_timeout else "on_brain_error"
        block = self._fallback.get(key) or {}
        if isinstance(block, dict):
            return str(block.get("reply") or "处理出现问题，请稍后重试。")
        return "处理出现问题，请稍后重试。"

    def plan_steps_from_brain(self, brain: BrainResponse) -> list[PlanStep]:
        decision = brain.decision
        if decision.confidence < 0.5:
            return []

        steps = list(decision.plan.steps)
        if self.mode == "brain_led":
            allowed = self.allowed_plugins
            if allowed:
                steps = [step for step in steps if step.plugin_id in allowed]
        return steps

    def immediate_reply(self, decision: BrainDecision) -> str | None:
        if decision.plan.steps:
            if decision.reply and decision.reply.text:
                return decision.reply.text
            return None
        if decision.reply and decision.reply.text:
            return decision.reply.text
        return None

    def evaluate_after_plugin(
        self,
        *,
        intent: str,
        verification: Verification,
        entities: dict[str, Any],
        session_vars: dict[str, Any],
    ) -> RouteOutcome | None:
        ctx = {
            "verification": verification.model_dump(mode="json"),
            "entities": entities,
            "session_vars": session_vars,
        }
        for route in self._routes:
            match = route.get("match") or {}
            if not isinstance(match, dict):
                continue
            route_intent = match.get("intent")
            if route_intent != intent:
                continue

            when = route.get("when")
            if when and not _eval_when(str(when), ctx):
                continue

            reply_block = route.get("reply")
            reply_text = None
            if isinstance(reply_block, dict):
                reply_text = reply_block.get("text")

            plugin_block = route.get("plugin")
            if plugin_block is None:
                return RouteOutcome(reply_text=reply_text)

            if isinstance(plugin_block, dict):
                params = dict(plugin_block.get("param_mapping") or {})
                resolved = _resolve_mapping(params, ctx)
                return RouteOutcome(
                    plugin_id=str(plugin_block.get("plugin_id") or ""),
                    command=str(plugin_block.get("command") or ""),
                    params=resolved,
                    reply_text=reply_text,
                    require_confirmation=bool(plugin_block.get("require_confirmation")),
                )

            if isinstance(plugin_block, str):
                return RouteOutcome(
                    plugin_id=plugin_block,
                    command="ping",
                    params={},
                    reply_text=reply_text,
                )

            return RouteOutcome(reply_text=reply_text)

        return None

    def default_reply_for_intent(self, intent: str) -> str | None:
        for route in self._routes:
            match = route.get("match") or {}
            if match.get("intent") != intent:
                continue
            reply = route.get("reply")
            if isinstance(reply, dict) and reply.get("text"):
                return str(reply["text"])
        return None


def _resolve_mapping(mapping: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    resolved: dict[str, Any] = {}
    for key, value in mapping.items():
        if isinstance(value, str) and value.startswith("$entities."):
            entity_key = value.removeprefix("$entities.")
            resolved[key] = ctx.get("entities", {}).get(entity_key)
        else:
            resolved[key] = value
    return resolved


def _eval_when(expr: str, ctx: dict[str, Any]) -> bool:
    expr = expr.strip()
    verification = ctx.get("verification") or {}

    match = re.fullmatch(r"\$verification\.passed\s*==\s*(true|false)", expr, flags=re.I)
    if match:
        expected = match.group(1).lower() == "true"
        return bool(verification.get("passed")) == expected

    match = re.fullmatch(r"\$verification\.evidence\.(\w+)\s*!=\s*null", expr, flags=re.I)
    if match:
        key = match.group(1)
        evidence = verification.get("evidence") or {}
        return evidence.get(key) is not None

    return True
