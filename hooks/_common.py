#!/usr/bin/env python3
"""Shared hook helpers for Cursor Loop Engineering."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

UNSAFE_PATTERNS = [
    re.compile(r"\brm\s+-rf\s+/\b"),
    re.compile(r"\bgit\s+push\s+.*--force\b"),
    re.compile(r"\bgit\s+reset\s+--hard\b"),
    re.compile(r"\bcurl\s+[^\n]*\|\s*(ba)?sh\b"),
    re.compile(r"\bdd\s+if=", re.I),
]

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)api[_-]?key\s*=\s*['\"][^'\"]{16,}"),
]


def read_payload() -> dict[str, Any]:
    raw = sys.stdin.read() or "{}"
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def emit(permission: str, message: str, **extra: Any) -> int:
    payload = {"permission": permission, "agent_message": message}
    payload.update(extra)
    print(json.dumps(payload))
    return 0 if permission == "allow" else 2


def command_text(payload: dict[str, Any]) -> str:
    for key in ("command", "cmd", "shell_command", "input"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    tool_input = payload.get("tool_input") or payload.get("arguments") or {}
    if isinstance(tool_input, dict):
        for key in ("command", "cmd", "content", "code"):
            value = tool_input.get(key)
            if isinstance(value, str):
                return value
    return json.dumps(payload)


def deny_if_unsafe(payload: dict[str, Any]) -> str | None:
    text = command_text(payload)
    for pattern in UNSAFE_PATTERNS:
        if pattern.search(text):
            return f"Denied unsafe pattern: {pattern.pattern}"
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            return "Denied potential secret material in tool input"
    return None


def append_event(message: str) -> None:
    root = Path.cwd()
    events = root / ".cursor-loop" / "events.jsonl"
    if not events.parent.exists():
        return
    record = {
        "event_type": "HOOK",
        "message": message,
        "source": Path(__file__).name,
    }
    with events.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
