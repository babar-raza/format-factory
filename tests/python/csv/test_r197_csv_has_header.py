"""
Tests for csv_has_header — sprint product-deepening-rnext66.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CSV_SAMPLES = REPO / "samples" / "by-format" / "csv"

sys.path.insert(0, str(REPO))

from src.python.ff_csv.csv_parser import csv_has_header


def test_import():
    assert callable(csv_has_header)


def test_minimal_2x2_has_header():
    result = csv_has_header(CSV_SAMPLES / "minimal-2x2.csv")
    assert result is True


def test_single_cell_has_header():
    result = csv_has_header(CSV_SAMPLES / "single-cell.csv")
    assert result is True


def test_quoted_fields_has_header():
    result = csv_has_header(CSV_SAMPLES / "quoted-fields.csv")
    assert result is True


def test_returns_bool():
    result = csv_has_header(CSV_SAMPLES / "minimal-2x2.csv")
    assert isinstance(result, bool)


def test_returns_bool_for_quoted():
    result = csv_has_header(CSV_SAMPLES / "quoted-fields.csv")
    assert isinstance(result, bool)
