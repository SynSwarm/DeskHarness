"""Run plugin handlers with timeout (local-script sandbox lite)."""

from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import Any, Callable

from pkg.plugin.handler import HandlerContext, HandlerResult


def run_handler_with_timeout(
    handler: Callable[[HandlerContext], HandlerResult],
    ctx: HandlerContext,
    *,
    timeout_ms: int,
) -> HandlerResult:
    timeout_sec = max(0.1, timeout_ms / 1000.0)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(handler, ctx)
        try:
            return future.result(timeout=timeout_sec)
        except FuturesTimeoutError:
            return HandlerResult(
                status="failure",
                passed=False,
                evidence={"plugin_id": ctx.plugin_id, "command": ctx.command, "timeout_ms": timeout_ms},
                failure_reason=f"handler timeout after {timeout_ms}ms",
            )
        except Exception as exc:
            return HandlerResult(
                status="failure",
                passed=False,
                evidence={"plugin_id": ctx.plugin_id, "command": ctx.command},
                failure_reason=str(exc),
            )


def run_handler_subprocess(
    plugin_root: Path,
    command_name: str,
    ctx: HandlerContext,
    *,
    timeout_ms: int,
) -> HandlerResult:
    payload = {
        "trace_id": ctx.trace_id,
        "turn_id": ctx.turn_id,
        "plugin_id": ctx.plugin_id,
        "command": ctx.command,
        "params": ctx.params,
        "session_vars": ctx.session_vars,
    }
    timeout_sec = max(0.1, timeout_ms / 1000.0)
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "core.plugin_subprocess",
            str(plugin_root),
            command_name,
        ],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        check=False,
    )
    if proc.returncode != 0:
        return HandlerResult(
            status="failure",
            passed=False,
            evidence={"plugin_id": ctx.plugin_id, "command": command_name, "stderr": proc.stderr[:500]},
            failure_reason=proc.stderr.strip() or f"subprocess exit {proc.returncode}",
        )
    try:
        data: dict[str, Any] = json.loads(proc.stdout)
        return HandlerResult(
            status=str(data.get("status") or "failure"),
            passed=bool((data.get("verification") or {}).get("passed")),
            evidence=dict((data.get("verification") or {}).get("evidence") or {}),
            failure_reason=(data.get("verification") or {}).get("failure_reason"),
            reply_text=((data.get("reply_override") or {}) or {}).get("text"),
        )
    except json.JSONDecodeError:
        return HandlerResult(
            status="failure",
            passed=False,
            evidence={"stdout": proc.stdout[:500]},
            failure_reason="invalid subprocess JSON output",
        )
