#!/usr/bin/env python3
"""Backward-compatible installer entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FRAMEWORK_ROOT / "runtime"))
sys.path.insert(0, str(FRAMEWORK_ROOT / "sdk"))

from cursor_loop_install.framework_core import install_into  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install Cursor Loop Engineering into a project")
    parser.add_argument("target", nargs="?", default=".", help="Target project directory")
    parser.add_argument("--force", action="store_true", help="Force update managed assets (still backs up first)")
    args = parser.parse_args(argv)
    try:
        result = install_into(Path(args.target), force=args.force)
    except Exception as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result.get("result") == "PASS" else 4


if __name__ == "__main__":
    raise SystemExit(main())
