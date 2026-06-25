"""Smoke tests for fodt/cli.py (TC-QF-R-002)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"


def test_main_is_callable():
    from fodt.cli import main
    assert callable(main)


def test_main_no_args_exits_zero(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ff-fodt"])
    from fodt.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_valid_file(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["ff-fodt", str(_SAMPLE)])
    from fodt.cli import main
    main()
    captured = capsys.readouterr()
    assert "Paragraph count" in captured.out or "paragraphs" in captured.out.lower() or "File" in captured.out


def test_main_missing_file_exits_nonzero(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["ff-fodt", "/no/such/file.fodt"])
    from fodt.cli import main
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code != 0
