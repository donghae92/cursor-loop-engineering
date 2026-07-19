#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, read_payload  # noqa: E402


def main() -> int:
    payload = read_payload()
    tool = payload.get("tool_name") or payload.get("tool") or "unknown"
    return emit(
        "allow",
        f"Cursor Loop post-task ({tool}): record evidence under .cursor-loop/; re-run cle verify after mutations.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
