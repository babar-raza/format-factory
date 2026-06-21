"""Tests for CSV Sprint 63 gap closure.

Closes:
  GAP-CSV-FOSS-CSV_COLUMN_U-001   (Csv Column Uniformity)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_column_uniformity

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE = str(_DIR / "single-cell.csv")


class TestCsvColumnUniformity:
    def test_return_type(self):
        assert isinstance(csv_column_uniformity(_MINIMAL), (int, float))

    def test_exact_1_0_for_minimal(self):
        assert csv_column_uniformity(_MINIMAL) == 1.0

    def test_exact_1_0_for_quoted(self):
        assert csv_column_uniformity(_QUOTED) == 1.0

    def test_exact_1_0_for_single(self):
        assert csv_column_uniformity(_SINGLE) == 1.0

    def test_between_0_and_1(self):
        assert 0.0 <= csv_column_uniformity(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert csv_column_uniformity(_MINIMAL) == csv_column_uniformity(_MINIMAL)
