#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    raw = sys.stdin.read() or "{}"
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        payload = {}
    events = Path.cwd() / ".cursor-loop" / "events.jsonl"
    events.parent.mkdir(parents=True, exist_ok=True)
    with events.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({
            "event_type": "TOOL_FAILURE",
            "payload_keys": sorted(list(payload.keys())),
        }) + "\n")
    print(json.dumps({
        "additional_context": "Cursor Loop failure hook recorded an event. Consider `python3 -m cursor_loop doctor`."
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
