"""Tests for cursor_loop CLI commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from cursor_loop.cli import main


@pytest.fixture
def cli_project(isolated_project: Path) -> Path:
    return isolated_project


def test_cli_bootstrap_initializes_runtime(cli_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["bootstrap", "--path", str(cli_project)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert payload["result"] == "PASS"
    assert (cli_project / ".cursor-loop" / "state.json").exists()
    assert (cli_project / ".cursor-loop" / "loop_state.json").exists()
    assert (cli_project / ".cursor-loop" / "checkpoints").is_dir()


def test_cli_status_reports_runtime(cli_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    main(["bootstrap", "--path", str(cli_project)])
    capsys.readouterr()

    rc = main(["status", "--path", str(cli_project)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert "state" in payload
    assert "loop_state" in payload
    assert "performance" in payload
    assert "schedule" in payload
    assert payload["state"]["phase"] in {"BOOTSTRAPPED", "HEALTHY"}


def test_cli_doctor_passes_for_bootstrapped_minimal_project(
    cli_project: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    main(["bootstrap", "--path", str(cli_project)])
    capsys.readouterr()

    rc = main(["doctor", "--path", str(cli_project)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert payload["project_root"] == str(cli_project.resolve())
    assert "python" in payload
    if sys.version_info >= (3, 9):
        assert rc == 0
        assert payload["result"] == "PASS"
        assert payload["issues"] == []
    else:
        assert rc == 4
        assert payload["result"] == "FAIL"
        assert any("Python 3.9+ required" in issue for issue in payload["issues"])


def test_cli_doctor_reports_missing_cursor(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["doctor", "--path", str(tmp_path)])
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 4
    assert payload["result"] == "FAIL"
    assert any(".cursor directory missing" in issue for issue in payload["issues"])


def test_cli_main_handles_unknown_command(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["unknown-command"])

    captured = capsys.readouterr()
    assert "usage:" in captured.err.lower() or captured.err
