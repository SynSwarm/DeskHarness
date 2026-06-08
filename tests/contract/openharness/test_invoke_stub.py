"""OpenHarness invoke stub contract tests."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from app.factory import create_app
from app.services.openharness_invoke import STUB_MODE_ENV, invoke_openharness, invoke_openharness_stub
from app.settings import EngineSettings

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "schemas" / "openharness" / "fixtures"
SCHEMAS = ROOT / "schemas" / "openharness"

MINIMAL_REQUEST = json.loads((FIXTURES / "minimal-request.json").read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _clear_stub_mode() -> None:
    os.environ.pop(STUB_MODE_ENV, None)
    yield
    os.environ.pop(STUB_MODE_ENV, None)


@pytest.fixture
def stub_settings() -> EngineSettings:
    return EngineSettings(openharness_invoke_mode="stub")


def test_minimal_request_roundtrip_stub() -> None:
    os.environ[STUB_MODE_ENV] = "minimal_200"
    body, status = invoke_openharness(dict(MINIMAL_REQUEST), settings=EngineSettings(openharness_invoke_mode="turn"))
    assert status == 200
    dumped = body.model_dump(mode="json")
    assert dumped["request_id"] == "req_minimal_001"
    assert dumped["response"]["status"] == "success"
    ads = dumped["response"]["action_directives"]
    assert len(ads) == 1
    assert ads[0]["action_type"] == "render_message"
    assert "Hello, OpenHarness." in ads[0]["payload"]["text"]


def test_protocol_version_unsupported_returns_error_envelope() -> None:
    bad = dict(MINIMAL_REQUEST)
    bad["protocol_version"] = "99.0.0"
    body, status = invoke_openharness_stub(bad)
    assert status == 200
    dumped = body.model_dump(mode="json")
    assert "error" in dumped
    assert dumped["error"]["code"] == "protocol_version_unsupported"


def test_stub_501_mode() -> None:
    os.environ[STUB_MODE_ENV] = "501"
    body, status = invoke_openharness({})
    assert status == 501
    assert "error" in body.model_dump(mode="json")


def test_http_health_and_invoke(stub_settings: EngineSettings) -> None:
    app = create_app(stub_settings)
    client = TestClient(app)
    prefix = app.state.settings.openharness_path_prefix

    health = client.get(f"{prefix}/health")
    assert health.status_code == 200
    assert health.json().get("stub") is True

    response = client.post(f"{prefix}/invoke", json=MINIMAL_REQUEST)
    assert response.status_code == 200
    data = response.json()
    assert data.get("request_id") == "req_minimal_001"
    assert data["response"]["action_directives"][0]["action_type"] == "render_message"


def test_response_matches_json_schema() -> None:
    os.environ[STUB_MODE_ENV] = "minimal_200"
    body, _ = invoke_openharness_stub(dict(MINIMAL_REQUEST))
    schema = json.loads((SCHEMAS / "invoke-response.v1.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(body.model_dump(mode="json")), key=lambda e: e.path)
    assert not errors, [e.message for e in errors]
