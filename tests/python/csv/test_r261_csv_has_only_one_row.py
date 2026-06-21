"""Tests for CSV Sprint 41 batch 3 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_HAS_ONLY-001  (Csv Has Only One Row)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_has_only_one_row

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvHasOnlyOneRow:
    def test_return_type(self):
        assert isinstance(csv_has_only_one_row(_MINIMAL_2X2), bool)

    def test_false_for_minimal_2x2(self):
        assert csv_has_only_one_row(_MINIMAL_2X2) is False

    def test_false_for_quoted_fields(self):
        assert csv_has_only_one_row(_QUOTED) is False

    def test_true_for_single_cell(self):
        assert csv_has_only_one_row(_SINGLE) is True

    def test_consistent_across_calls(self):
        assert csv_has_only_one_row(_MINIMAL_2X2) == csv_has_only_one_row(_MINIMAL_2X2)
