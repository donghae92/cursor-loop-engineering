#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, read_payload  # noqa: E402


def main() -> int:
    _ = read_payload()
    return emit(
        "allow",
        "Cursor Loop continue: only after measurable progress; identical failures → SAFE_STOP.",
    )


if __name__ == "__main__":
    raise SystemExit(main())
