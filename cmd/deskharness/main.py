"""Go-style launcher: `python cmd/deskharness/main.py serve`."""

from __future__ import annotations

from app.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
