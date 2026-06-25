"""Smoke tests for gnumeric/cli.py (TC-QF-R-002)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"


def test_main_is_callable():
    from gnumeric.cli import main
    assert callable(main)


def test_main_no_args_exits_zero(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ff-gnumeric"])
    from gnumeric.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_valid_file(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["ff-gnumeric", str(_SAMPLE)])
    from gnumeric.cli import main
    main()
    captured = capsys.readouterr()
    assert "Sheet count" in captured.out or "File" in captured.out


def test_main_missing_file_exits_nonzero(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ff-gnumeric", "/no/such/file.gnumeric"])
    from gnumeric.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code != 0
