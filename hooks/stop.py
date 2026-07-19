#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    _ = sys.stdin.read()
    loop_path = Path.cwd() / ".cursor-loop" / "loop_state.json"
    out = {}
    if loop_path.exists():
        state = json.loads(loop_path.read_text(encoding="utf-8"))
        disp = state.get("disposition")
        if disp == "CONTINUE" and state.get("last_result") == "FAIL":
            out["followup_message"] = "Cursor Loop: failed gate remains. Run cle repair && cle verify."
        elif disp in {"SAFE_STOP", "MANUAL_REVIEW"}:
            out["followup_message"] = f"Cursor Loop {disp}: stop identical failure loops and await review if needed."
    print(json.dumps(out))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
