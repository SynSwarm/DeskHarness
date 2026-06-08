"""Phase 1 turn loop integration tests."""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.factory import create_app
from app.services.runtime import build_turn_engine
from app.settings import EngineSettings, load_settings
from core.session_store import SessionStore

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "schemas" / "openharness" / "fixtures"
MINIMAL_REQUEST = json.loads((FIXTURES / "minimal-request.json").read_text(encoding="utf-8"))


@pytest.fixture
def turn_settings(tmp_path: Path) -> EngineSettings:
    base = load_settings("configs/config.template.yaml")
    return replace(
        base,
        openharness_invoke_mode="turn",
        session_store_path=tmp_path / "test.db",
        routes_file=ROOT / "configs" / "routes.yaml",
    )


def test_turn_minimal_request_matches_gold_sample(turn_settings: EngineSettings) -> None:
    engine = build_turn_engine(turn_settings)
    body, status = engine.process(dict(MINIMAL_REQUEST))
    assert status == 200
    dumped = body.model_dump(mode="json")
    assert dumped["request_id"] == "req_minimal_001"
    assert dumped["response"]["action_directives"][0]["payload"]["text"] == "Hello, OpenHarness."


def test_turn_persists_session(turn_settings: EngineSettings) -> None:
    engine = build_turn_engine(turn_settings)
    engine.process(dict(MINIMAL_REQUEST))
    store = SessionStore(turn_settings.session_store_path)
    session = store.get("sess_demo")
    assert session is not None
    assert len(session.recent_turns) == 1
    assert session.recent_turns[0]["input"] == "Hello, OpenHarness."


def test_turn_noop_dispatch_via_mock_brain(turn_settings: EngineSettings) -> None:
    engine = build_turn_engine(turn_settings)
    payload = copy.deepcopy(MINIMAL_REQUEST)
    payload["request"]["context"]["user_intent"] = "please trigger-noop now"

    body, status = engine.process(payload)
    assert status == 200
    text = body.model_dump(mode="json")["response"]["action_directives"][0]["payload"]["text"]
    assert "理解" in text or "noop" in text.lower()


def test_http_turn_mode_health(turn_settings: EngineSettings) -> None:
    app = create_app(turn_settings)
    client = TestClient(app)
    prefix = app.state.settings.openharness_path_prefix

    health = client.get(f"{prefix}/health")
    assert health.status_code == 200
    assert health.json()["invoke_mode"] == "turn"
    assert health.json()["stub"] is False

    response = client.post(f"{prefix}/invoke", json=MINIMAL_REQUEST)
    assert response.status_code == 200
    assert (
        response.json()["response"]["action_directives"][0]["payload"]["text"]
        == "Hello, OpenHarness."
    )
