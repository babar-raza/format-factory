"""Smoke tests for toml/cli.py (TC-QF-R-002)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"


def test_main_is_callable():
    from toml.cli import main
    assert callable(main)


def test_main_no_args_exits_zero(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ff-toml"])
    from toml.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_valid_file(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["ff-toml", str(_SAMPLE)])
    from toml.cli import main
    main()
    captured = capsys.readouterr()
    assert "Sections" in captured.out or "Total keys" in captured.out or "File" in captured.out


def test_main_missing_file_exits_nonzero(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ff-toml", "/no/such/file.toml"])
    from toml.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code != 0
