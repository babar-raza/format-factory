"""Smoke tests for fods/cli.py (TC-QF-R-002)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"


def test_main_is_callable():
    from fods.cli import main
    assert callable(main)


def test_main_no_args_exits_zero(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ff-fods"])
    from fods.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_valid_file(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["ff-fods", str(_SAMPLE)])
    from fods.cli import main
    main()  # should return normally
    captured = capsys.readouterr()
    assert "Sheet count" in captured.out


def test_main_missing_file_exits_nonzero(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ff-fods", "/no/such/file.fods"])
    from fods.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code != 0
