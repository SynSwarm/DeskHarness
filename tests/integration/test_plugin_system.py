"""Plugin loader and shell integration tests."""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.factory import create_app
from app.services.runtime import build_plugin_registry, build_turn_engine
from app.settings import EngineSettings, load_settings
from core.plugin_loader import PluginRegistry

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
        routes_file=ROOT / "configs/routes.yaml",
        plugin_dirs=(ROOT / "plugins",),
    )


def test_registry_loads_noop_echo_and_webhook_shell(turn_settings: EngineSettings) -> None:
    registry = build_plugin_registry(turn_settings)
    assert "noop" in registry.list_plugin_ids()
    assert "echo" in registry.list_plugin_ids()
    assert "webhook-generic" in registry.list_shell_ids()
    assert registry.get_plugin("noop").handlers["ping"] is not None


def test_echo_dispatch_via_turn_engine(turn_settings: EngineSettings) -> None:
    engine = build_turn_engine(turn_settings)
    payload = copy.deepcopy(MINIMAL_REQUEST)
    payload["request"]["context"]["user_intent"] = "trigger-echo: hello echo"

    body, status = engine.process(payload)
    assert status == 200
    text = body.model_dump(mode="json")["response"]["action_directives"][0]["payload"]["text"]
    assert "hello echo" in text


def test_webhook_shell_inbound_http(turn_settings: EngineSettings) -> None:
    app = create_app(turn_settings)
    client = TestClient(app)

    response = client.post(
        "/shells/webhook-generic/inbound",
        json={"text": "Hello from webhook", "session_id": "sess_webhook_001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["reply"] == "Hello from webhook"
