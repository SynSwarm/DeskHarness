"""Optional HTTP mock brain for manual testing (`brain.adapter: http`)."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.schemas.brain import BrainRequest
from core.brain_client import MockBrainClient


class _Handler(BaseHTTPRequestHandler):
    client = MockBrainClient()

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length)
        request = BrainRequest.model_validate(json.loads(raw))
        response = self.client.complete(request)
        body = json.dumps(response.model_dump(mode="json")).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    host, port = "127.0.0.1", 8090
    server = HTTPServer((host, port), _Handler)
    print(f"mock brain listening on http://{host}:{port}/brain")
    server.serve_forever()


if __name__ == "__main__":
    main()
