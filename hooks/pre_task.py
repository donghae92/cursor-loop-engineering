#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import deny_if_unsafe, emit, read_payload  # noqa: E402


def main() -> int:
    payload = read_payload()
    denied = deny_if_unsafe(payload)
    if denied:
        return emit("deny", f"Cursor Loop pre-task blocked: {denied}")
    tool = payload.get("tool_name") or payload.get("tool") or "unknown"
    return emit(
        "allow",
        f"Cursor Loop pre-task ({tool}): prefer cle verify/status; write runtime under .cursor-loop/ only.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
