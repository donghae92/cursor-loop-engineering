#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, read_payload  # noqa: E402


def main() -> int:
    payload = read_payload()
    status = payload.get("status") or payload.get("disposition") or "unknown"
    return emit(
        "allow",
        f"Cursor Loop stop hook ({status}): persist disposition under .cursor-loop/loop_state.json.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
