"""Tests for csv_total_cell_count().

Sprint: product-deepening-rnext83
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import csv_total_cell_count

CSV_SAMPLES = _REPO / "samples" / "by-format" / "csv"


class TestCsvTotalCellCount:
    def test_import(self):
        assert callable(csv_total_cell_count)

    def test_minimal_2x2_has_four_cells(self):
        assert csv_total_cell_count(CSV_SAMPLES / "minimal-2x2.csv") == 4

    def test_single_cell_has_one(self):
        assert csv_total_cell_count(CSV_SAMPLES / "single-cell.csv") == 1

    def test_quoted_fields_has_six(self):
        assert csv_total_cell_count(CSV_SAMPLES / "quoted-fields.csv") == 6

    def test_returns_int(self):
        result = csv_total_cell_count(CSV_SAMPLES / "minimal-2x2.csv")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for sample in CSV_SAMPLES.iterdir():
            if sample.suffix == ".csv" and "invalid" not in sample.name:
                assert csv_total_cell_count(sample) >= 0
