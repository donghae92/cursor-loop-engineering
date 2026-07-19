"""Tests for framework install_into using real assets."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from cursor_loop_runtime.models import read_json


def _load_install_module(framework_root: Path):
    install_path = framework_root / "install" / "install.py"
    spec = importlib.util.spec_from_file_location("cle_install", install_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_install_into_copies_assets_and_manifest(tmp_path: Path, framework_root: Path) -> None:
    install_mod = _load_install_module(framework_root)

    result = install_mod.install_into(tmp_path)

    assert result["result"] == "PASS"
    assert result["file_count"] > 0
    assert (tmp_path / ".cursor" / "hooks.json").exists()
    assert (tmp_path / ".cursor" / "rules").is_dir()
    assert (tmp_path / ".cursor" / "skills").is_dir()
    assert (tmp_path / ".cursor" / "agents").is_dir()
    assert (tmp_path / ".cursor" / "hooks").is_dir()
    assert (tmp_path / ".cursor-loop" / "state.json").exists()
    assert (tmp_path / "AGENTS.md").exists()

    manifest = read_json(tmp_path / ".cursor-loop" / "install_manifest.json", {})
    assert manifest["framework"] == "cursor-loop-engineering"
    assert manifest["version"] == "1.1.0"
    assert len(manifest.get("files", [])) == result["file_count"]


def test_install_into_makes_hook_scripts_executable(tmp_path: Path, framework_root: Path) -> None:
    install_mod = _load_install_module(framework_root)

    install_mod.install_into(tmp_path)

    hooks_dir = tmp_path / ".cursor" / "hooks"
    scripts = list(hooks_dir.glob("*.py"))
    assert scripts
    for script in scripts:
        assert script.stat().st_mode & 0o111


def test_install_into_idempotent_with_force(tmp_path: Path, framework_root: Path) -> None:
    install_mod = _load_install_module(framework_root)

    first = install_mod.install_into(tmp_path)
    second = install_mod.install_into(tmp_path, force=True)

    assert first["result"] == "PASS"
    assert second["result"] == "PASS"
    assert second["file_count"] == first["file_count"]
