"""Shell adapter base contract."""

from __future__ import annotations

from typing import Any, Protocol


class ShellAdapter(Protocol):
    shell_id: str

    def to_invoke_request(self, raw: dict[str, Any]) -> dict[str, Any]: ...

    def from_invoke_response(self, response: dict[str, Any]) -> dict[str, Any]: ...
