"""Subprocess entry: load plugins/<id>/handler.py and run one command."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from pkg.plugin.handler import HandlerContext


def main() -> int:
    if len(sys.argv) != 3:
        print(json.dumps({"status": "failure", "verification": {"passed": False, "failure_reason": "usage"}}))
        return 1

    plugin_root = Path(sys.argv[1])
    command_name = sys.argv[2]
    raw = sys.stdin.read()
    payload = json.loads(raw) if raw.strip() else {}

    module_path = plugin_root / "handler.py"
    spec = importlib.util.spec_from_file_location("plugin_handler", module_path)
    if spec is None or spec.loader is None:
        print(json.dumps({"status": "failure", "verification": {"passed": False, "failure_reason": "no handler"}}))
        return 1

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handler = getattr(module, command_name, None)
    if not callable(handler):
        print(json.dumps({"status": "failure", "verification": {"passed": False, "failure_reason": "no command"}}))
        return 1

    ctx = HandlerContext(
        trace_id=str(payload.get("trace_id") or ""),
        turn_id=str(payload.get("turn_id") or ""),
        plugin_id=str(payload.get("plugin_id") or ""),
        command=command_name,
        params=dict(payload.get("params") or {}),
        session_vars=dict(payload.get("session_vars") or {}),
    )
    result = handler(ctx)
    print(json.dumps(result.to_plugin_result_dict(ctx.trace_id)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
