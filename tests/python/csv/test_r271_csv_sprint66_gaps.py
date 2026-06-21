"""Tests for CSV Sprint 66 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_HAS_ONLY-001   (Csv Has Only Numeric Row)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_has_only_numeric_row

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvHasOnlyNumericRow:
    def test_return_type(self):
        assert isinstance(csv_has_only_numeric_row(_MINIMAL), bool)

    def test_false_for_minimal(self):
        assert csv_has_only_numeric_row(_MINIMAL) is False

    def test_false_for_quoted(self):
        assert csv_has_only_numeric_row(_QUOTED) is False

    def test_true_for_single_numeric(self):
        # single-cell.csv has header "value" and data "42" — only numeric row
        assert csv_has_only_numeric_row(_SINGLE) is True

    def test_is_boolean(self):
        result = csv_has_only_numeric_row(_MINIMAL)
        assert result in (True, False)

    def test_consistent_across_calls(self):
        assert csv_has_only_numeric_row(_MINIMAL) == csv_has_only_numeric_row(_MINIMAL)
