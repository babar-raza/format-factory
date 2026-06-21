"""Tests for gnumeric_multi_sheet_ratio — closing GAP-Gnumeric-FOSS-GNUMERIC_MUL-001."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_multi_sheet_ratio

SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"


def test_multi_sheet_ratio_returns_float():
    result = gnumeric_multi_sheet_ratio(SAMPLES / "minimal-spreadsheet.gnumeric")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_multi_sheet_ratio_multi_cell():
    result = gnumeric_multi_sheet_ratio(SAMPLES / "multi-cell-basic.gnumeric")
    assert isinstance(result, float)


def test_multi_sheet_ratio_empty_sheet():
    result = gnumeric_multi_sheet_ratio(SAMPLES / "empty-sheet.gnumeric")
    assert isinstance(result, float)
    assert result >= 0.0
