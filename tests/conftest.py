"""Shared pytest fixtures for Cursor Loop Engineering tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

MINIMAL_HOOKS_JSON = {
    "version": 1,
    "hooks": {},
}


@pytest.fixture
def framework_root() -> Path:
    from cursor_loop.paths import framework_root as get_root

    return get_root()


@pytest.fixture
def minimal_hooks_json() -> dict:
    return dict(MINIMAL_HOOKS_JSON)


@pytest.fixture
def isolated_project(tmp_path: Path, minimal_hooks_json: dict) -> Path:
    """Temporary project root with minimal .cursor layout."""
    cursor = tmp_path / ".cursor"
    for name in ("rules", "skills", "agents", "hooks", "templates", "examples"):
        (cursor / name).mkdir(parents=True)
    (cursor / "hooks.json").write_text(
        json.dumps(minimal_hooks_json, indent=2) + "\n",
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture
def bootstrapped_project(isolated_project: Path) -> Path:
    """Isolated project with runtime memory initialized."""
    from cursor_loop_runtime.memory_controller import MemoryController
    from cursor_loop_runtime.state_machine import StateMachine

    MemoryController(isolated_project).ensure()
    StateMachine(isolated_project).mark_healthy("test bootstrap")
    return isolated_project
