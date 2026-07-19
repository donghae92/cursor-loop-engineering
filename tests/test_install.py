"""Tests for installer using the production sdk installer package."""

from __future__ import annotations

from pathlib import Path

from cursor_loop_install.framework_core import install_into
from cursor_loop_install.versions import read_framework_version


def test_install_into_copies_assets_and_manifest(tmp_path: Path) -> None:
    result = install_into(tmp_path, force=True)
    assert result["result"] == "PASS"
    assert (tmp_path / ".cursor" / "hooks.json").exists()
    assert (tmp_path / ".cursor" / "skills").is_dir()
    assert (tmp_path / ".cursor" / "agents").is_dir()
    assert (tmp_path / ".cursor" / "commands").is_dir()
    manifest = tmp_path / ".cursor-loop" / "install_manifest.json"
    assert manifest.exists()
    assert read_framework_version() == "2.0.0"


def test_install_into_makes_hook_scripts_executable(tmp_path: Path) -> None:
    install_into(tmp_path, force=True)
    hooks = list((tmp_path / ".cursor" / "hooks").glob("*.py"))
    assert hooks
    for script in hooks:
        assert script.stat().st_mode & 0o111


def test_install_into_idempotent_with_force(tmp_path: Path) -> None:
    first = install_into(tmp_path, force=True)
    second = install_into(tmp_path, force=True)
    assert first["result"] == "PASS"
    assert second["result"] == "PASS"
