"""Build Brain client from engine settings."""

from __future__ import annotations

from app.settings import EngineSettings
from core.brain_client import HttpBrainClient, MockBrainClient
from core.brain_prompt_template import PromptTemplateBrainClient


def build_brain_client(settings: EngineSettings):
    if settings.brain_adapter == "http":
        return HttpBrainClient(
            settings.brain_endpoint,
            timeout_ms=settings.brain_timeout_ms,
        )
    if settings.brain_adapter == "prompt-template":
        return PromptTemplateBrainClient.from_file(settings.brain_template_file)
    return MockBrainClient()
