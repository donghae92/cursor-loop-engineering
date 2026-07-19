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
        return emit("deny", f"Cursor Loop validation blocked: {denied}")
    return emit(
        "allow",
        "Cursor Loop validation: require durable artifacts; model confidence is not evidence.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
