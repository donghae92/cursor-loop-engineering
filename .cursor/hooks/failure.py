#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import append_event, emit, read_payload  # noqa: E402


def main() -> int:
    payload = read_payload()
    message = str(payload.get("message") or payload.get("error") or "failure event")
    append_event(f"failure: {message}")
    return emit(
        "allow",
        "Cursor Loop failure hook: localize section, cle doctor --repair, cle loop --once, then cle verify.",
        failure=message,
    )


if __name__ == "__main__":
    raise SystemExit(main())
