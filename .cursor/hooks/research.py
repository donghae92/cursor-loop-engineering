#!/usr/bin/env python3
import json, sys

def main() -> int:
    _ = sys.stdin.read()
    print(json.dumps({
        "additional_context": "Cursor Loop research: cite paths; do not mutate; separate observation from interpretation."
    }))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
