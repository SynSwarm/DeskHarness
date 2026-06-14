"""Turn orchestration: OH invoke → Session → Brain → Plugin → outbound."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.schemas.brain import BrainContext, BrainInput, BrainRequest
from app.schemas.openharness import (
    SUPPORTED_PROTOCOL_VERSIONS,
    OpenHarnessActionDirective,
    OpenHarnessErrorBody,
    OpenHarnessInvokeErrorResponse,
    OpenHarnessInvokeRequest,
    OpenHarnessInvokeResponse,
    OpenHarnessResponsePayload,
)
from app.schemas.plugin import PluginCommand
from app.schemas.session import Session
from core.brain_client import BrainClient
from core.dispatcher import PluginDispatcher
from core.metrics import EngineMetrics
from core.router import Router
from core.runtime.compaction import compact_session_context
from core.session.protocol import SessionStoreProtocol
from core.structured_log import StructuredLogger


class TurnEngine:
    def __init__(
        self,
        *,
        session_store: SessionStoreProtocol,
        brain_client: BrainClient,
        router: Router,
        dispatcher: PluginDispatcher,
        logger: StructuredLogger | None = None,
        metrics: EngineMetrics | None = None,
        context_max_turns: int = 20,
        context_keep_recent: int = 10,
    ) -> None:
        self._sessions = session_store
        self._brain = brain_client
        self._router = router
        self._dispatcher = dispatcher
        self._logger = logger
        self._metrics = metrics
        self._context_max_turns = context_max_turns
        self._context_keep_recent = context_keep_recent

    def process(self, body: dict[str, Any]) -> tuple[OpenHarnessInvokeResponse | OpenHarnessInvokeErrorResponse, int]:
        req = OpenHarnessInvokeRequest.model_validate(body)
        if req.protocol_version not in SUPPORTED_PROTOCOL_VERSIONS:
            return self._protocol_error(req), 200

        oh_request = req.request if isinstance(req.request, dict) else {}
        ctx = oh_request.get("context") if isinstance(oh_request.get("context"), dict) else {}

        session = self._resolve_session(ctx)
        compact_session_context(
            session,
            max_turns=self._context_max_turns,
            keep_recent=self._context_keep_recent,
        )
        turn_id = f"turn_{uuid4().hex[:12]}"
        trace_id = (req.correlation_id or req.request_id or turn_id).strip() or turn_id
        user_intent = str(ctx.get("user_intent") or "").strip()

        brain_request = BrainRequest(
            trace_id=trace_id,
            turn_id=turn_id,
            session_id=session.session_id,
            input=BrainInput(type="text", text=user_intent),
            context=BrainContext(
                recent_turns=list(session.recent_turns),
                session_vars=dict(session.session_vars),
            ),
            available_intents=self._router.available_intents(),
        )

        try:
            brain_response = self._brain.complete(brain_request)
        except Exception:
            if self._metrics:
                self._metrics.inc_brain_error()
            text = self._router.brain_fallback_reply(on_timeout=False)
            return self._success(req, text, trace_id=trace_id), 200

        decision = brain_response.decision
        if decision.confidence < 0.5:
            text = self._router.brain_fallback_reply(on_timeout=True)
            return self._success(req, text, trace_id=trace_id), 200

        steps = self._router.plan_steps_from_brain(brain_response)
        final_text = self._router.immediate_reply(decision) or user_intent or "Hello, OpenHarness."
        plugin_ids: list[str] = []

        route_outcome = None
        if steps:
            for step in steps:
                plugin_ids.append(step.plugin_id)
                command = PluginCommand(
                    trace_id=trace_id,
                    turn_id=turn_id,
                    plugin_id=step.plugin_id,
                    command=step.command,
                    params=dict(step.params),
                    session_vars=dict(session.session_vars),
                )
                result = self._dispatcher.dispatch(command)

                route_outcome = self._router.evaluate_after_plugin(
                    intent=decision.intent,
                    verification=result.verification,
                    entities=decision.entities,
                    session_vars=session.session_vars,
                )
                if route_outcome and route_outcome.reply_text:
                    final_text = route_outcome.reply_text
                elif result.reply_override and result.reply_override.get("text"):
                    final_text = str(result.reply_override["text"])

            if not (route_outcome and route_outcome.reply_text) and not result.verification.passed:
                route_default = self._router.default_reply_for_intent(decision.intent)
                if route_default:
                    final_text = route_default

        self._record_turn(session, turn_id=turn_id, trace_id=trace_id, user_intent=user_intent, reply=final_text)
        self._sessions.save(session)

        if self._metrics:
            self._metrics.inc_turn()
        if self._logger:
            self._logger.log_turn_completed(
                trace_id=trace_id,
                turn_id=turn_id,
                session_id=session.session_id,
                intent=decision.intent,
                plugin_ids=plugin_ids,
                reply=final_text,
            )

        return self._success(req, final_text, trace_id=trace_id), 200

    def _resolve_session(self, ctx: dict[str, Any]) -> Session:
        session_id = str(ctx.get("session_id") or "").strip() or None
        shell_id = str(ctx.get("shell_id") or "webhook-generic")
        channel_user_id = str(ctx.get("channel_user_id") or ctx.get("session_id") or "").strip()
        display_name = str(ctx.get("display_name") or "")
        return self._sessions.get_or_create(
            session_id=session_id,
            shell_id=shell_id,
            channel_user_id=channel_user_id or "anonymous",
            display_name=display_name,
        )

    @staticmethod
    def _record_turn(
        session: Session,
        *,
        turn_id: str,
        trace_id: str,
        user_intent: str,
        reply: str,
    ) -> None:
        session.recent_turns.append(
            {
                "turn_id": turn_id,
                "trace_id": trace_id,
                "input": user_intent,
                "reply": reply,
            }
        )
        if len(session.recent_turns) > 20:
            session.recent_turns[:] = session.recent_turns[-20:]

    @staticmethod
    def _success(
        req: OpenHarnessInvokeRequest,
        text: str,
        *,
        trace_id: str,
    ) -> OpenHarnessInvokeResponse:
        return OpenHarnessInvokeResponse(
            protocol_version="1.0.0",
            request_id=req.request_id or trace_id,
            supported_protocol_versions=list(SUPPORTED_PROTOCOL_VERSIONS),
            response=OpenHarnessResponsePayload(
                status="success",
                action_directives=[
                    OpenHarnessActionDirective(
                        action_type="render_message",
                        payload={"text": text},
                    )
                ],
            ),
        )

    @staticmethod
    def _protocol_error(req: OpenHarnessInvokeRequest) -> OpenHarnessInvokeErrorResponse:
        return OpenHarnessInvokeErrorResponse(
            protocol_version="1.0.0",
            request_id=req.request_id or "req_error",
            supported_protocol_versions=list(SUPPORTED_PROTOCOL_VERSIONS),
            error=OpenHarnessErrorBody(
                code="protocol_version_unsupported",
                message=(
                    f"supported: {', '.join(SUPPORTED_PROTOCOL_VERSIONS)}; "
                    f"got: {req.protocol_version!r}"
                ),
                retryable=False,
            ),
        )
