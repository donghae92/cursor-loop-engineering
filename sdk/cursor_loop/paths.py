"""Framework paths and repository root discovery."""

from __future__ import annotations

from pathlib import Path


def framework_root() -> Path:
    """Return the cursor-loop-engineering repository root."""
    return Path(__file__).resolve().parents[2]


def ensure_sys_path() -> Path:
    import sys

    root = framework_root()
    for path in (str(root / "runtime"), str(root / "sdk")):
        if path not in sys.path:
            sys.path.insert(0, path)
    return root
