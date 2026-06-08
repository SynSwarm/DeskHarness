"""Pytest bootstrap: local `cmd/` shadows stdlib `cmd` on editable installs."""

from __future__ import annotations

import importlib.util
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path


def _install_stdlib_cmd() -> None:
    root = Path(__file__).resolve().parents[1]
    local_cmd = root / "cmd"
    spec = importlib.util.find_spec("cmd")
    if not spec or not spec.submodule_search_locations:
        return

    locs = {Path(p).resolve() for p in spec.submodule_search_locations}
    if local_cmd.resolve() not in locs:
        return

    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    stdlib_cmd = Path(sys.base_prefix) / "lib" / f"python{py_ver}" / "cmd.py"
    if not stdlib_cmd.is_file():
        return

    loader = SourceFileLoader("cmd", str(stdlib_cmd))
    module = importlib.util.module_from_spec(importlib.util.spec_from_loader("cmd", loader))
    assert module is not None
    loader.exec_module(module)
    sys.modules["cmd"] = module


_install_stdlib_cmd()
