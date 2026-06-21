"""
Tests for additional CSV analytics gap closure (2 FOSS gaps).
Closes: GAP-CSV-FOSS-CSV_HEADER_L-001, GAP-CSV-FOSS-CSV_EMPTY_FI-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_header_length_sum,
    csv_empty_field_ratio,
)

_CSV_2x2 = _REPO / "samples/by-format/csv/minimal-2x2.csv"
_CSV_QUOTED = _REPO / "samples/by-format/csv/quoted-fields.csv"
_CSV_SINGLE = _REPO / "samples/by-format/csv/single-cell.csv"


class TestCsvHeaderLengthSum:
    def test_returns_int(self):
        assert isinstance(csv_header_length_sum(_CSV_2x2), int)

    def test_nonnegative(self):
        assert csv_header_length_sum(_CSV_2x2) >= 0

    def test_2x2_exact(self):
        # minimal-2x2 has headers; sum of header cell lengths = 7
        assert csv_header_length_sum(_CSV_2x2) == 7

    def test_single_cell_nonnegative(self):
        assert csv_header_length_sum(_CSV_SINGLE) >= 0


class TestCsvEmptyFieldRatio:
    def test_returns_float(self):
        assert isinstance(csv_empty_field_ratio(_CSV_2x2), float)

    def test_bounded(self):
        assert 0.0 <= csv_empty_field_ratio(_CSV_2x2) <= 1.0

    def test_full_content_zero_ratio(self):
        # minimal-2x2 has no empty fields
        assert csv_empty_field_ratio(_CSV_2x2) == pytest.approx(0.0)

    def test_single_cell_nonnegative(self):
        assert csv_empty_field_ratio(_CSV_SINGLE) >= 0.0
