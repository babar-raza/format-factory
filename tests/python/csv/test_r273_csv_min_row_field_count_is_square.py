"""Tests for csv_min_row_field_count and csv_is_square (Sprint 63)."""
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_min_row_field_count, csv_is_square

CSV = _REPO / "samples" / "by-format" / "csv"


class TestCsvMinRowFieldCount:
    def test_minimal_2x2(self):
        assert csv_min_row_field_count(CSV / "minimal-2x2.csv") == 2

    def test_quoted_fields(self):
        assert csv_min_row_field_count(CSV / "quoted-fields.csv") == 3

    def test_single_cell(self):
        assert csv_min_row_field_count(CSV / "single-cell.csv") == 1

    def test_returns_int(self):
        assert isinstance(csv_min_row_field_count(CSV / "minimal-2x2.csv"), int)

    def test_positive(self):
        for f in ["minimal-2x2.csv", "quoted-fields.csv", "single-cell.csv"]:
            assert csv_min_row_field_count(CSV / f) > 0


class TestCsvIsSquare:
    def test_minimal_2x2_is_square(self):
        assert csv_is_square(CSV / "minimal-2x2.csv") is True

    def test_quoted_fields_not_square(self):
        assert csv_is_square(CSV / "quoted-fields.csv") is False

    def test_single_cell_is_square(self):
        assert csv_is_square(CSV / "single-cell.csv") is True

    def test_returns_bool(self):
        assert isinstance(csv_is_square(CSV / "minimal-2x2.csv"), bool)

    def test_false_for_non_square(self):
        assert csv_is_square(CSV / "quoted-fields.csv") is False
