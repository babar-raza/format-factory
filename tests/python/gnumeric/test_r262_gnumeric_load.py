"""Tests for Gnumeric load capability.

Closes:
  GAP-Gnumeric-FOSS-LOAD-001  (Gnumeric Load)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import load as gnumeric_load

_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_EMPTY = str(_DIR / "empty-sheet.gnumeric")
_MULTI = str(_DIR / "multi-cell-basic.gnumeric")
_MINIMAL = str(_DIR / "minimal-spreadsheet.gnumeric")


class TestGnumericLoad:
    def test_return_type(self):
        result = gnumeric_load(_EMPTY)
        assert isinstance(result, dict)

    def test_is_gnumeric_true(self):
        result = gnumeric_load(_EMPTY)
        assert result["is_gnumeric"] is True

    def test_sheet_count_1_for_empty(self):
        result = gnumeric_load(_EMPTY)
        assert result["sheet_count"] == 1

    def test_cell_count_0_for_empty(self):
        result = gnumeric_load(_EMPTY)
        assert result["cell_count"] == 0

    def test_cell_count_4_for_multi(self):
        result = gnumeric_load(_MULTI)
        assert result["cell_count"] == 4

    def test_has_sheets_key(self):
        result = gnumeric_load(_EMPTY)
        assert "sheets" in result

    def test_consistent_across_calls(self):
        r1 = gnumeric_load(_MULTI)
        r2 = gnumeric_load(_MULTI)
        assert r1["cell_count"] == r2["cell_count"]
