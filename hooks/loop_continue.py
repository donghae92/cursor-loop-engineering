#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    _ = sys.stdin.read()
    root = Path.cwd()
    loop_path = root / ".cursor-loop" / "loop_state.json"
    out = {}
    if loop_path.exists():
        state = json.loads(loop_path.read_text(encoding="utf-8"))
        if state.get("disposition") == "CONTINUE":
            out["followup_message"] = (
                "Cursor Loop CONTINUE: run `python3 -m cursor_loop repair` then "
                "`python3 -m cursor_loop loop --once`."
            )
    print(json.dumps(out))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
