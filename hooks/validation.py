#!/usr/bin/env python3
import json, sys
from pathlib import Path

def main() -> int:
    _ = sys.stdin.read()
    verify = Path.cwd() / ".cursor-loop" / "last_verify.json"
    msg = "Cursor Loop validation: run `python3 -m cursor_loop verify`."
    if verify.exists():
        data = json.loads(verify.read_text(encoding="utf-8"))
        msg = f"Last verify result={data.get('result')} failures={data.get('failure_count')}"
    print(json.dumps({"additional_context": msg}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
