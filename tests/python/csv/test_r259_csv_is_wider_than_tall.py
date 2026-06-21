"""Tests for csv_is_wider_than_tall (Sprint 40 batch 4).

Closes:
  GAP-CSV-FOSS-CSV_IS_WIDER-001  (Csv Is Wider Than Tall)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_is_wider_than_tall

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.csv")
_QUOTED_FIELDS = str(_DIR / "quoted-fields.csv")
_SINGLE_CELL = str(_DIR / "single-cell.csv")


class TestCsvIsWiderThanTall:
    def test_return_type(self):
        assert isinstance(csv_is_wider_than_tall(_MINIMAL_2X2), bool)

    def test_false_for_minimal_2x2(self):
        # 2 rows x 2 cols -> not wider
        assert csv_is_wider_than_tall(_MINIMAL_2X2) is False

    def test_true_for_quoted_fields(self):
        # more columns than rows -> wider
        assert csv_is_wider_than_tall(_QUOTED_FIELDS) is True

    def test_false_for_single_cell(self):
        # 1x1 -> not wider
        assert csv_is_wider_than_tall(_SINGLE_CELL) is False

    def test_consistent_across_calls(self):
        assert csv_is_wider_than_tall(_MINIMAL_2X2) == csv_is_wider_than_tall(_MINIMAL_2X2)
