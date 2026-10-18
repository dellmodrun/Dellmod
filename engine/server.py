"""Minimal HTTP server: serves the static site and a JSON telemetry API.

Runs with only the Python standard library (no framework) so the container
image stays tiny.

Routes
------
- ``/``, ``/index.html``, ``/terminal.html``, ``/assets/*`` — the static site
- ``/api/network`` — live telemetry snapshot (same shape as ``data.json``)
- ``/api/health``  — liveness probe

Usage::

    python -m engine.server              # http://localhost:8777
    PORT=9000 python -m engine.server
"""
from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from . import __version__, network

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.split("?")[0] == "/api/network":
            return self._json(network.build_snapshot())
        if self.path.split("?")[0] == "/api/health":
            return self._json({"status": "ok", "version": __version__})
        return super().do_GET()

    def log_message(self, fmt, *args):  # quieter logs
        return


def main() -> None:
    port = int(os.environ.get("PORT", "8777"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Dellmod engine v{__version__} serving on http://0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover
        server.shutdown()


if __name__ == "__main__":
    main()
