"""DeskHarness CLI entry."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="deskharness")
    sub = parser.add_subparsers(dest="command", required=True)

    serve = sub.add_parser("serve", help="Start Engine HTTP server")
    serve.add_argument("--host", default=None)
    serve.add_argument("--port", type=int, default=None)
    serve.add_argument(
        "--config",
        default="configs/config.yaml",
        help="Path to config.yaml (falls back to config.template.yaml)",
    )

    plugin = sub.add_parser("plugin", help="Plugin scaffolding")
    plugin_sub = plugin.add_subparsers(dest="plugin_command", required=True)
    plugin_new = plugin_sub.add_parser("new", help="Create a new plugin or shell directory")
    plugin_new.add_argument("plugin_id", help="Plugin id, e.g. my-bot")
    plugin_new.add_argument(
        "--type",
        choices=("plugin", "shell"),
        default="plugin",
        help="plugin (default) or shell",
    )
    plugin_new.add_argument(
        "--handler",
        default="run",
        help="Default handler function / command name",
    )
    plugin_new.add_argument(
        "--output-dir",
        default="plugins",
        help="Parent directory for plugins/<id>/",
    )

    args = parser.parse_args(argv)

    if args.command == "serve":
        import uvicorn

        from app.factory import create_app
        from app.settings import load_settings

        settings = load_settings(args.config)
        host = args.host or settings.host
        port = args.port or settings.port
        app = create_app(settings)

        uvicorn.run(app, host=host, port=port, log_level="info")
        return 0

    if args.command == "plugin" and args.plugin_command == "new":
        from pathlib import Path

        from app.plugin_scaffold import create_plugin

        try:
            root = create_plugin(
                plugin_id=args.plugin_id,
                plugin_type=args.type,
                output_dir=Path(args.output_dir),
                command=args.handler,
            )
        except (ValueError, FileExistsError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

        print(f"created {root}")
        return 0

    return 0
