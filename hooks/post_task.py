#!/usr/bin/env python3
import json, sys

def main() -> int:
    _ = sys.stdin.read()
    print(json.dumps({
        "additional_context": "Cursor Loop post-task: after derived changes run `python3 -m cursor_loop verify`."
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
