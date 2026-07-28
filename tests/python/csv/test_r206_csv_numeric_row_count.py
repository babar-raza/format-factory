"""
Tests for csv_numeric_row_count — sprint product-deepening-rnext75.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CSV_SAMPLES = REPO / "samples" / "by-format" / "csv"

sys.path.insert(0, str(REPO))

from src.python.ff_csv.csv_parser import csv_numeric_row_count


def test_import():
    assert callable(csv_numeric_row_count)


def test_minimal_2x2_no_numeric_rows():
    result = csv_numeric_row_count(CSV_SAMPLES / "minimal-2x2.csv")
    assert result == 0


def test_single_cell_one_numeric_row():
    result = csv_numeric_row_count(CSV_SAMPLES / "single-cell.csv")
    assert result == 1


def test_quoted_fields_no_numeric_rows():
    result = csv_numeric_row_count(CSV_SAMPLES / "quoted-fields.csv")
    assert result == 0


def test_returns_int():
    result = csv_numeric_row_count(CSV_SAMPLES / "minimal-2x2.csv")
    assert isinstance(result, int)


def test_result_nonnegative():
    result = csv_numeric_row_count(CSV_SAMPLES / "single-cell.csv")
    assert result >= 0
