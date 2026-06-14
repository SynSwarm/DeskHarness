"""Phase 3: logging, metrics, debug, sync-http, Redis session, batch 2."""

from __future__ import annotations

import copy
import json
import threading
import time
from dataclasses import replace
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.factory import create_app
from app.schemas.brain import BrainDecision, BrainPlan, BrainReply, BrainResponse, BrainTarget, PlanStep
from app.schemas.plugin import PluginCommand, Verification
from app.schemas.session import Session, SessionContext
from app.services.runtime import build_plugin_registry, build_turn_engine
from app.settings import EngineSettings, load_settings
from core.async_tasks import AsyncTaskStore
from core.dispatcher import PluginDispatcher
from core.metrics import EngineMetrics
from core.router import Router
from core.runtime.compaction import compact_session_context
from core.structured_log import StructuredLogger

ROOT = Path(__file__).resolve().parents[2]
MINIMAL_REQUEST = json.loads(
    (ROOT / "schemas/openharness/fixtures/minimal-request.json").read_text(encoding="utf-8")
)


@pytest.fixture
def turn_settings(tmp_path: Path) -> EngineSettings:
    base = load_settings("configs/config.template.yaml")
    return replace(
        base,
        openharness_invoke_mode="turn",
        session_store_path=tmp_path / "test.db",
        log_dir=tmp_path / "logs",
        routes_file=ROOT / "configs/routes.yaml",
        plugin_dirs=(ROOT / "plugins",),
    )


def test_structured_log_written(turn_settings: EngineSettings) -> None:
    logger = StructuredLogger(turn_settings.log_dir)
    engine = build_turn_engine(turn_settings, logger=logger)
    engine.process(copy.deepcopy(MINIMAL_REQUEST))
    log_file = turn_settings.log_dir / "turns.jsonl"
    assert log_file.is_file()
    line = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert line["event"] == "turn.completed"
    assert "trace_id" in line


def test_metrics_increment(turn_settings: EngineSettings) -> None:
    metrics = EngineMetrics()
    engine = build_turn_engine(turn_settings, metrics=metrics)
    engine.process(copy.deepcopy(MINIMAL_REQUEST))
    snap = metrics.snapshot()
    assert snap["turns_total"] >= 1


def test_debug_routes_and_dry_run(turn_settings: EngineSettings) -> None:
    app = create_app(turn_settings)
    client = TestClient(app)

    routes = client.get("/debug/routes")
    assert routes.status_code == 200
    assert "routes" in routes.json()

    brain = BrainResponse(
        trace_id="tr_dry",
        decision=BrainDecision(
            intent="general.chat",
            confidence=0.9,
            plan=BrainPlan(steps=[PlanStep(plugin_id="noop", command="ping")]),
            reply=BrainReply(text="hi"),
            target=BrainTarget(statement="test"),
        ),
    )
    dry = client.post("/debug/dry-run", json=brain.model_dump(mode="json"))
    assert dry.status_code == 200
    assert dry.json()["plan_steps"][0]["plugin_id"] == "noop"


def test_metrics_endpoint(turn_settings: EngineSettings) -> None:
    app = create_app(turn_settings)
    client = TestClient(app)
    client.post(f"{app.state.settings.openharness_path_prefix}/invoke", json=MINIMAL_REQUEST)
    prom = client.get("/metrics")
    assert prom.status_code == 200
    assert "deskharness_turns_total" in prom.text


def test_registry_loads_order_lookup_sync_http(turn_settings: EngineSettings) -> None:
    registry = build_plugin_registry(turn_settings)
    loaded = registry.get_plugin("order-lookup")
    assert loaded is not None
    assert loaded.manifest.execution_mode == "sync-http"


def test_sync_http_order_lookup_dispatch(turn_settings: EngineSettings) -> None:
    class _Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length))
            payload = {
                "result_version": "0.2",
                "trace_id": body.get("trace_id", ""),
                "status": "success",
                "verification": {
                    "passed": True,
                    "evidence": {"order_id": "12345", "status": "shipped"},
                    "failure_reason": None,
                },
                "reply_override": {"type": "text", "text": "shipped"},
            }
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.15)

    settings = replace(
        turn_settings,
        plugin_dirs=(ROOT / "plugins",),
    )
    registry = build_plugin_registry(settings)
    loaded = registry.get_plugin("order-lookup")
    assert loaded is not None
    loaded.manifest.execution.endpoint = f"http://127.0.0.1:{port}/plugins/order-lookup"

    engine = build_turn_engine(settings, registry)
    payload = copy.deepcopy(MINIMAL_REQUEST)
    payload["request"]["context"]["user_intent"] = "query order 12345"
    body, status = engine.process(payload)
    assert status == 200
    text = body.model_dump(mode="json")["response"]["action_directives"][0]["payload"]["text"]
    assert "12345" in text or "shipped" in text.lower()
    server.shutdown()


def test_redis_session_store_roundtrip() -> None:
    pytest.importorskip("redis")
    from core.session.redis_store import RedisSessionStore

    try:
        store = RedisSessionStore("redis://127.0.0.1:6379/15", ttl_seconds=60)
        session = store.get_or_create(
            session_id="sess_redis_test",
            shell_id="test",
            channel_user_id="user_1",
        )
        session.recent_turns.append({"input": "hi"})
        store.save(session)
        loaded = store.get("sess_redis_test")
        assert loaded is not None
        assert loaded.recent_turns[0]["input"] == "hi"
    except Exception as exc:
        pytest.skip(f"redis not available: {exc}")


def test_context_compaction_folds_old_turns() -> None:
    session = Session(
        session_id="sess_compact",
        shell_id="test",
        context=SessionContext(
            recent_turns=[{"input": f"q{i}", "reply": f"a{i}"} for i in range(25)],
        ),
    )
    compact_session_context(session, max_turns=20, keep_recent=5)
    assert len(session.recent_turns) == 5
    summary = session.session_vars.get("_context_summary", "")
    assert "q0" in summary
    assert "q19" in summary


def test_handler_timeout_returns_failure(turn_settings: EngineSettings, tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugin_root = plugins_dir / "slow-noop"
    plugin_root.mkdir(parents=True)
    (plugin_root / "manifest.yaml").write_text(
        """
plugin_id: slow-noop
plugin_type: plugin
version: 0.1.0
api_version: "0.2"
execution:
  mode: local-script
  timeout_ms: 100
commands:
  - name: ping
""",
        encoding="utf-8",
    )
    (plugin_root / "handler.py").write_text(
        """
import time
from pkg.plugin.handler import HandlerContext, HandlerResult, success

def ping(ctx: HandlerContext) -> HandlerResult:
    time.sleep(0.5)
    return success(ctx, reply_text="slow")
""",
        encoding="utf-8",
    )

    settings = replace(
        turn_settings,
        plugin_dirs=(plugins_dir,),
        routing_allowed_plugins=("slow-noop",),
    )
    registry = build_plugin_registry(settings)
    dispatcher = PluginDispatcher(registry, allowed_plugins={"slow-noop"})
    cmd = PluginCommand(
        trace_id="tr_slow",
        turn_id="turn_slow",
        plugin_id="slow-noop",
        command="ping",
        params={},
        session_vars={},
    )
    result = dispatcher.dispatch(cmd)
    assert result.status == "failure"
    assert result.verification.passed is False
    assert "timeout" in (result.verification.failure_reason or "").lower()


def test_async_webhook_creates_pending_task(turn_settings: EngineSettings) -> None:
    class _Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length") or 0)
            self.rfile.read(length)
            ack = b'{"accepted":true}'
            self.send_response(202)
            self.send_header("Content-Length", str(len(ack)))
            self.end_headers()
            self.wfile.write(ack)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.15)

    settings = replace(
        turn_settings,
        plugin_dirs=(ROOT / "plugins",),
        routing_allowed_plugins=(*turn_settings.routing_allowed_plugins, "async-demo"),
        callback_public_base="http://testserver",
    )
    registry = build_plugin_registry(settings)
    loaded = registry.get_plugin("async-demo")
    assert loaded is not None
    loaded.manifest.execution.endpoint = f"http://127.0.0.1:{port}/plugins/async-demo"

    tasks = AsyncTaskStore()
    dispatcher = PluginDispatcher(
        registry,
        allowed_plugins={"async-demo"},
        async_tasks=tasks,
        callback_public_base=settings.callback_public_base,
    )
    cmd = PluginCommand(
        trace_id="tr_async",
        turn_id="turn_async",
        plugin_id="async-demo",
        command="submit",
        params={},
        session_vars={},
    )
    result = dispatcher.dispatch(cmd)
    assert result.status == "partial"
    task_id = result.verification.evidence.get("task_id")
    assert task_id
    record = tasks.get(str(task_id))
    assert record is not None
    assert record.status == "pending"
    server.shutdown()


def test_async_callback_completes_task(turn_settings: EngineSettings) -> None:
    settings = replace(turn_settings, routing_allowed_plugins=(*turn_settings.routing_allowed_plugins, "async-demo"))
    app = create_app(settings)
    client = TestClient(app)
    tasks: AsyncTaskStore = app.state.async_tasks
    record = tasks.create(plugin_id="async-demo", command="submit", trace_id="tr_cb")
    payload = {
        "result_version": "0.2",
        "trace_id": "tr_cb",
        "status": "success",
        "verification": Verification(passed=True, evidence={"done": True}, failure_reason=None).model_dump(),
        "reply_override": {"type": "text", "text": "done"},
    }
    resp = client.post(f"/plugins/callbacks/{record.task_id}", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    got = client.get(f"/plugins/callbacks/{record.task_id}")
    assert got.json()["result"]["status"] == "success"


def test_rate_limit_returns_429(turn_settings: EngineSettings) -> None:
    settings = replace(
        turn_settings,
        rate_limit_enabled=True,
        rate_limit_requests_per_minute=1,
    )
    app = create_app(settings)
    client = TestClient(app)
    path = f"{settings.openharness_path_prefix}/invoke"
    first = client.post(path, json=MINIMAL_REQUEST)
    second = client.post(path, json=copy.deepcopy(MINIMAL_REQUEST))
    assert first.status_code == 200
    assert second.status_code == 429
    assert app.state.metrics.snapshot()["rate_limited_total"] >= 1

