"""Brain HTTP / mock clients."""

from __future__ import annotations

from typing import Protocol

import httpx

from app.schemas.brain import (
    BrainDecision,
    BrainPlan,
    BrainReply,
    BrainRequest,
    BrainResponse,
    BrainTarget,
    PlanStep,
)


class BrainClient(Protocol):
    def complete(self, request: BrainRequest) -> BrainResponse: ...


class MockBrainClient:
    """Phase 1 in-process brain for local dev and tests."""

    CONFIDENCE_THRESHOLD = 0.5

    def complete(self, request: BrainRequest) -> BrainResponse:
        text = (request.input.text or "").strip()
        lower = text.lower()

        if "trigger-noop" in lower:
            return self._response(
                request,
                intent="system.unknown",
                confidence=0.9,
                steps=[PlanStep(plugin_id="noop", command="ping")],
                reply_text="正在执行 noop 健康检查…",
            )

        if "trigger-echo" in lower:
            message = text.split(":", 1)[1].strip() if ":" in text else text.replace("trigger-echo", "").strip()
            return self._response(
                request,
                intent="general.chat",
                confidence=0.95,
                steps=[PlanStep(plugin_id="echo", command="echo", params={"message": message or "echo"})],
                reply_text="正在回显…",
            )

        if "order" in lower and any(ch.isdigit() for ch in text):
            order_id = "".join(ch for ch in text if ch.isdigit())
            return self._response(
                request,
                intent="order.query",
                confidence=0.92,
                steps=[
                    PlanStep(
                        plugin_id="order-lookup",
                        command="query",
                        params={"order_id": order_id},
                    )
                ],
                entities={"order_id": order_id},
                reply_text=f"正在为您查询订单 {order_id}…",
                target_statement=f"用户获知订单 {order_id} 状态",
            )

        return self._response(
            request,
            intent="general.chat",
            confidence=0.95,
            steps=[],
            reply_text=text or "Hello, OpenHarness.",
        )

    @staticmethod
    def _response(
        request: BrainRequest,
        *,
        intent: str,
        confidence: float,
        steps: list[PlanStep],
        reply_text: str,
        entities: dict | None = None,
        target_statement: str = "",
    ) -> BrainResponse:
        return BrainResponse(
            trace_id=request.trace_id,
            decision=BrainDecision(
                target=BrainTarget(statement=target_statement or reply_text),
                intent=intent,
                confidence=confidence,
                entities=entities or {},
                plan=BrainPlan(steps=steps),
                reply=BrainReply(text=reply_text),
            ),
        )


class HttpBrainClient:
    def __init__(self, endpoint: str, timeout_ms: int = 30_000) -> None:
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout_ms / 1000.0

    def complete(self, request: BrainRequest) -> BrainResponse:
        payload = request.model_dump(mode="json")
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(self.endpoint, json=payload)
            response.raise_for_status()
            return BrainResponse.model_validate(response.json())
