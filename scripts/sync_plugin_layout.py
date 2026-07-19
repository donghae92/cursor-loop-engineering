#!/usr/bin/env python3
"""Sync `.cursor/` workspace assets into Cursor plugin component directories."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "sdk"))
sys.path.insert(0, str(ROOT / "install"))

from cursor_loop_install.plugin import sync_plugin_layout, validate_plugin  # noqa: E402


def main() -> int:
    sync = sync_plugin_layout(ROOT)
    validation = validate_plugin(ROOT)
    print(json.dumps({"sync": sync, "validation": validation}, indent=2))
    return 0 if validation.get("result") == "PASS" else 4


if __name__ == "__main__":
    raise SystemExit(main())
