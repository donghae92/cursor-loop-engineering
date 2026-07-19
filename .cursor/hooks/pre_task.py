#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    raw = sys.stdin.read() or "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}
    tool = payload.get("tool_name") or payload.get("tool") or ""
    print(json.dumps({
        "permission": "allow",
        "agent_message": f"Cursor Loop pre-task ({tool}): prefer cle verify/status; write runtime under .cursor-loop/ only."
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
