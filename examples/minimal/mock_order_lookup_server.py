"""Mock sync-http order-lookup plugin for local demos."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        command = self.path.rstrip("/").split("/")[-1]
        body = json.loads(raw) if raw else {}
        params = body.get("params") or {}
        order_id = str(params.get("order_id") or "unknown")
        trace_id = str(body.get("trace_id") or "")

        if command == "query":
            payload = {
                "result_version": "0.2",
                "trace_id": trace_id,
                "status": "success",
                "verification": {
                    "passed": True,
                    "evidence": {
                        "order_id": order_id,
                        "status": "shipped",
                        "eta": "2026-06-10",
                    },
                    "failure_reason": None,
                },
                "error": None,
                "reply_override": {
                    "type": "text",
                    "text": f"Order {order_id} is shipped, ETA 2026-06-10.",
                },
            }
        else:
            payload = {
                "result_version": "0.2",
                "trace_id": trace_id,
                "status": "failure",
                "verification": {
                    "passed": False,
                    "evidence": {"order_id": order_id, "command": command},
                    "failure_reason": f"unsupported command: {command}",
                },
                "error": None,
                "reply_override": None,
            }

        data = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    host, port = "127.0.0.1", 8091
    server = HTTPServer((host, port), _Handler)
    print(f"mock order-lookup listening on http://{host}:{port}/plugins/order-lookup/{{command}}")
    server.serve_forever()


if __name__ == "__main__":
    main()
