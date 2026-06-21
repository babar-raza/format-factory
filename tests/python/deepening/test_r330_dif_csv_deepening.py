"""Sprint 120 — DIF (dif_bytes_per_cell, dif_bytes_per_tuple)
and CSV (csv_bytes_per_field, csv_bytes_per_row).
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import dif_bytes_per_cell, dif_bytes_per_tuple
from src.python.csv.csv_parser import csv_bytes_per_field, csv_bytes_per_row

DIF = _REPO / "samples" / "by-format" / "dif" / "valid"
CSV = _REPO / "samples" / "by-format" / "csv"


# ---------- dif_bytes_per_cell ----------

class TestDifBytesPerCell:
    def test_minimal_value(self):
        assert abs(dif_bytes_per_cell(DIF / "minimal-2x2.dif") - 23.375) < 0.01

    def test_numeric_value(self):
        assert abs(dif_bytes_per_cell(DIF / "numeric-row.dif") - 41.0) < 0.01

    def test_single_value(self):
        assert abs(dif_bytes_per_cell(DIF / "single-cell.dif") - 108.0) < 0.01

    def test_returns_float(self):
        assert isinstance(dif_bytes_per_cell(DIF / "minimal-2x2.dif"), float)

    def test_positive(self):
        assert dif_bytes_per_cell(DIF / "minimal-2x2.dif") > 0.0


# ---------- dif_bytes_per_tuple ----------

class TestDifBytesPerTuple:
    def test_minimal_value(self):
        assert abs(dif_bytes_per_tuple(DIF / "minimal-2x2.dif") - 93.5) < 0.01

    def test_numeric_value(self):
        assert abs(dif_bytes_per_tuple(DIF / "numeric-row.dif") - 123.0) < 0.01

    def test_single_value(self):
        assert abs(dif_bytes_per_tuple(DIF / "single-cell.dif") - 108.0) < 0.01

    def test_returns_float(self):
        assert isinstance(dif_bytes_per_tuple(DIF / "minimal-2x2.dif"), float)

    def test_positive(self):
        assert dif_bytes_per_tuple(DIF / "numeric-row.dif") > 0.0


# ---------- csv_bytes_per_field ----------

class TestCsvBytesPerField:
    def test_minimal_value(self):
        assert abs(csv_bytes_per_field(CSV / "minimal-2x2.csv") - 6.25) < 0.01

    def test_quoted_value(self):
        assert abs(csv_bytes_per_field(CSV / "quoted-fields.csv") - 16.333) < 0.01

    def test_single_value(self):
        assert abs(csv_bytes_per_field(CSV / "single-cell.csv") - 9.0) < 0.01

    def test_returns_float(self):
        assert isinstance(csv_bytes_per_field(CSV / "minimal-2x2.csv"), float)

    def test_positive(self):
        assert csv_bytes_per_field(CSV / "minimal-2x2.csv") > 0.0


# ---------- csv_bytes_per_row ----------

class TestCsvBytesPerRow:
    def test_minimal_value(self):
        assert abs(csv_bytes_per_row(CSV / "minimal-2x2.csv") - 12.5) < 0.01

    def test_quoted_value(self):
        assert abs(csv_bytes_per_row(CSV / "quoted-fields.csv") - 49.0) < 0.01

    def test_single_value(self):
        assert abs(csv_bytes_per_row(CSV / "single-cell.csv") - 9.0) < 0.01

    def test_returns_float(self):
        assert isinstance(csv_bytes_per_row(CSV / "minimal-2x2.csv"), float)

    def test_positive(self):
        assert csv_bytes_per_row(CSV / "quoted-fields.csv") > 0.0
