"""Phase 2 remaining features: prompt-template, scaffold, brain rules."""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.factory import create_app
from app.plugin_scaffold import create_plugin
from app.services.runtime import build_turn_engine
from app.settings import EngineSettings, load_settings
from core.brain_prompt_template import PromptTemplateBrainClient

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


def test_prompt_template_general_chat(turn_settings: EngineSettings) -> None:
    settings = replace(
        turn_settings,
        brain_adapter="prompt-template",
        brain_template_file=ROOT / "configs/brain.prompt-template.yaml",
    )
    engine = build_turn_engine(settings)
    body, status = engine.process(copy.deepcopy(MINIMAL_REQUEST))
    assert status == 200
    text = body.model_dump(mode="json")["response"]["action_directives"][0]["payload"]["text"]
    assert text == "Hello, OpenHarness."


def test_prompt_template_noop_rule(turn_settings: EngineSettings) -> None:
    client = PromptTemplateBrainClient.from_file(ROOT / "configs/brain.prompt-template.yaml")
    from app.schemas.brain import BrainInput, BrainRequest

    request = BrainRequest(
        trace_id="tr_test",
        turn_id="turn_test",
        session_id="sess_test",
        input=BrainInput(text="please trigger-noop"),
    )
    response = client.complete(request)
    assert response.decision.intent == "system.unknown"
    assert response.decision.plan.steps[0].plugin_id == "noop"


def test_plugin_scaffold_creates_plugin(tmp_path: Path) -> None:
    root = create_plugin(
        plugin_id="demo-bot",
        plugin_type="plugin",
        output_dir=tmp_path,
        command="run",
    )
    assert (root / "manifest.yaml").is_file()
    assert (root / "handler.py").is_file()
    assert "plugin_id: demo-bot" in (root / "manifest.yaml").read_text(encoding="utf-8")


def test_plugin_scaffold_creates_shell(tmp_path: Path) -> None:
    root = create_plugin(
        plugin_id="demo-shell",
        plugin_type="shell",
        output_dir=tmp_path,
    )
    assert (root / "adapter.py").is_file()
    assert "class DemoShell" in (root / "adapter.py").read_text(encoding="utf-8")


def test_cli_plugin_new(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    from app.cli import main

    code = main(["plugin", "new", "hello-plugin", "--output-dir", "plugins"])
    assert code == 0
    assert (tmp_path / "plugins/hello-plugin/handler.py").is_file()


def test_docker_compose_files_exist() -> None:
    assert (ROOT / "Dockerfile").is_file()
    assert (ROOT / "configs/config.docker.yaml").is_file()
    assert (ROOT / "CHANGELOG.md").is_file()
    assert (ROOT / "doc/deployment/release.md").is_file()
    assert (ROOT / "examples/minimal/docker-compose.yml").is_file()
    assert (ROOT / "examples/minimal/docker-compose.image.yml").is_file()
    assert (ROOT / ".github/workflows/docker-publish.yml").is_file()
