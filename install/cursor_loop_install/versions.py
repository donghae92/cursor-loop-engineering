"""Version and path helpers for the installer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def framework_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_framework_version(root: Path | None = None) -> str:
    root = root or framework_root()
    version_file = root / "VERSION"
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "0.0.0"


def read_compatibility(root: Path | None = None) -> dict[str, Any]:
    root = root or framework_root()
    path = root / "COMPATIBILITY.json"
    if not path.exists():
        return {"framework": "cursor-loop-engineering", "current_version": read_framework_version(root), "matrix": []}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_semver(version: str) -> tuple[int, int, int]:
    parts = version.strip().lstrip("v").split(".")
    nums = []
    for part in parts[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        nums.append(int(digits or "0"))
    while len(nums) < 3:
        nums.append(0)
    return nums[0], nums[1], nums[2]


def compare_semver(a: str, b: str) -> int:
    left = parse_semver(a)
    right = parse_semver(b)
    if left < right:
        return -1
    if left > right:
        return 1
    return 0


ASSET_DIRS = ("rules", "skills", "agents", "hooks", "commands", "templates", "examples")
MANAGED_MARKER = "cursor-loop-engineering"
