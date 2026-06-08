"""Rule-based prompt-template Brain adapter (no LLM)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app.schemas.brain import (
    BrainDecision,
    BrainPlan,
    BrainReply,
    BrainRequest,
    BrainResponse,
    BrainTarget,
    PlanStep,
)


@dataclass(frozen=True)
class PromptRule:
    rule_id: str
    intent: str
    confidence: float
    reply: str
    contains: str | None = None
    regex: str | None = None
    entities: dict[str, str] | None = None
    plan: list[dict[str, Any]] | None = None


class PromptTemplateBrainClient:
    """Match user text against YAML rules; render templates into BrainResponse."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._default_intent = str(config.get("default_intent") or "general.chat")
        self._default_confidence = float(config.get("default_confidence") or 0.9)
        self._default_reply = str(config.get("default_reply") or "You said: {text}")
        self._rules = self._parse_rules(config.get("rules") or [])

    @classmethod
    def from_file(cls, path: Path) -> PromptTemplateBrainClient:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            msg = f"invalid prompt-template config: {path}"
            raise ValueError(msg)
        return cls(raw)

    def complete(self, request: BrainRequest) -> BrainResponse:
        text = (request.input.text or "").strip()
        context = self._build_context(text)

        for rule in self._rules:
            if not self._matches(rule, text, context):
                continue
            return self._build_response(request, rule, context)

        return BrainResponse(
            trace_id=request.trace_id,
            decision=BrainDecision(
                target=BrainTarget(statement=self._render(self._default_reply, context)),
                intent=self._default_intent,
                confidence=self._default_confidence,
                plan=BrainPlan(steps=[]),
                reply=BrainReply(text=self._render(self._default_reply, context)),
            ),
        )

    def _build_response(
        self,
        request: BrainRequest,
        rule: PromptRule,
        context: dict[str, Any],
    ) -> BrainResponse:
        entities = {
            key: self._render(str(value), context)
            for key, value in (rule.entities or {}).items()
        }
        context = {**context, **entities}

        steps: list[PlanStep] = []
        for item in rule.plan or []:
            if not isinstance(item, dict):
                continue
            params = item.get("params") or {}
            rendered_params = {
                str(key): self._render(str(value), context)
                for key, value in params.items()
            }
            steps.append(
                PlanStep(
                    plugin_id=str(item.get("plugin_id") or ""),
                    command=str(item.get("command") or ""),
                    params=rendered_params,
                )
            )

        reply_text = self._render(rule.reply, context)
        return BrainResponse(
            trace_id=request.trace_id,
            decision=BrainDecision(
                target=BrainTarget(statement=reply_text),
                intent=rule.intent,
                confidence=rule.confidence,
                entities=entities,
                plan=BrainPlan(steps=steps),
                reply=BrainReply(text=reply_text),
            ),
        )

    @staticmethod
    def _parse_rules(raw_rules: Any) -> list[PromptRule]:
        rules: list[PromptRule] = []
        if not isinstance(raw_rules, list):
            return rules
        for index, item in enumerate(raw_rules):
            if not isinstance(item, dict):
                continue
            rules.append(
                PromptRule(
                    rule_id=str(item.get("id") or f"rule_{index}"),
                    intent=str(item.get("intent") or "general.chat"),
                    confidence=float(item.get("confidence") or 0.9),
                    reply=str(item.get("reply") or "{text}"),
                    contains=str(item["contains"]) if item.get("contains") else None,
                    regex=str(item["regex"]) if item.get("regex") else None,
                    entities=dict(item.get("entities") or {}) or None,
                    plan=list(item.get("plan") or []) or None,
                )
            )
        return rules

    @staticmethod
    def _build_context(text: str) -> dict[str, Any]:
        after_colon = text.split(":", 1)[1].strip() if ":" in text else text
        return {
            "text": text,
            "text_after_colon": after_colon,
            "text_lower": text.lower(),
        }

    @staticmethod
    def _matches(rule: PromptRule, text: str, context: dict[str, Any]) -> bool:
        if rule.contains and rule.contains.lower() not in context["text_lower"]:
            return False
        if rule.regex:
            match = re.search(rule.regex, text, flags=re.I)
            if not match:
                return False
            for index, group in enumerate(match.groups(), start=1):
                context[f"match_group_{index}"] = group or ""
            return True
        if rule.contains:
            return True
        return rule.rule_id == "general_chat" or not rule.contains and not rule.regex

    @staticmethod
    def _render(template: str, context: dict[str, Any]) -> str:
        try:
            return template.format(**context)
        except KeyError:
            return template
