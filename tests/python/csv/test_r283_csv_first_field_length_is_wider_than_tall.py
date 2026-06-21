"""Tests for csv_first_field_length and csv_is_wider_than_tall (Sprint 73)."""
import pytest
from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_first_field_length, csv_is_wider_than_tall

CSV = _REPO / "samples" / "by-format" / "csv"


class TestCsvFirstFieldLength:
    def test_minimal_2x2(self):
        assert csv_first_field_length(CSV / "minimal-2x2.csv") == 5

    def test_quoted_fields(self):
        assert csv_first_field_length(CSV / "quoted-fields.csv") == 8

    def test_single_cell(self):
        assert csv_first_field_length(CSV / "single-cell.csv") == 2

    def test_returns_int(self):
        assert isinstance(csv_first_field_length(CSV / "minimal-2x2.csv"), int)

    def test_nonnegative(self):
        for f in ["minimal-2x2.csv", "quoted-fields.csv", "single-cell.csv"]:
            assert csv_first_field_length(CSV / f) >= 0


class TestCsvIsWiderThanTall:
    def test_square_minimal(self):
        assert csv_is_wider_than_tall(CSV / "minimal-2x2.csv") is False

    def test_wider_quoted(self):
        assert csv_is_wider_than_tall(CSV / "quoted-fields.csv") is True

    def test_square_single(self):
        assert csv_is_wider_than_tall(CSV / "single-cell.csv") is False

    def test_returns_bool(self):
        assert isinstance(csv_is_wider_than_tall(CSV / "minimal-2x2.csv"), bool)

    def test_all_files_return_bool(self):
        for f in ["minimal-2x2.csv", "quoted-fields.csv", "single-cell.csv"]:
            assert isinstance(csv_is_wider_than_tall(CSV / f), bool)
