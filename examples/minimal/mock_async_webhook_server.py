"""Mock async-webhook plugin server for examples and local dev."""

from __future__ import annotations

import json
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length))
        callback_url = str(body.get("callback_url") or "")

        def _callback() -> None:
            time.sleep(0.2)
            if not callback_url:
                return
            payload = {
                "result_version": "0.2",
                "trace_id": body.get("trace_id", ""),
                "status": "success",
                "verification": {
                    "passed": True,
                    "evidence": {"async": True, "plugin_id": "async-demo"},
                    "failure_reason": None,
                },
                "reply_override": {"type": "text", "text": "async task completed"},
            }
            req = urllib.request.Request(
                callback_url,
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=5)

        threading.Thread(target=_callback, daemon=True).start()

        ack = json.dumps({"accepted": True}).encode()
        self.send_response(202)
        self.send_header("Content-Length", str(len(ack)))
        self.end_headers()
        self.wfile.write(ack)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    host = "127.0.0.1"
    port = 8092
    server = HTTPServer((host, port), _Handler)
    print(f"async-demo mock listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
