"""
tests/python/fods/test_r182_fods_numeric_density.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT50-001
Tests for workbook_numeric_density() — ratio of numeric cells to total non-empty cells.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.parser import parse_fods_strict
from src.python.fods.neutral_model import workbook_numeric_density

SAMPLES = _REPO / "samples" / "by-format" / "fods"


class TestFodsNumericDensity:
    def test_typed_values_partial_numeric(self):
        wb = parse_fods_strict(SAMPLES / "typed-values-basic.fods")
        result = workbook_numeric_density(wb)
        assert 0.0 < result <= 1.0

    def test_minimal_spreadsheet_no_numerics(self):
        wb = parse_fods_strict(SAMPLES / "minimal-spreadsheet.fods")
        result = workbook_numeric_density(wb)
        assert result == 0.0

    def test_returns_float(self):
        wb = parse_fods_strict(SAMPLES / "typed-values-basic.fods")
        result = workbook_numeric_density(wb)
        assert isinstance(result, float)

    def test_in_range_zero_to_one(self):
        wb = parse_fods_strict(SAMPLES / "typed-values-basic.fods")
        result = workbook_numeric_density(wb)
        assert 0.0 <= result <= 1.0

    def test_empty_workbook_returns_zero(self):
        wb = {"sheets": []}
        result = workbook_numeric_density(wb)
        assert result == 0.0

    def test_exported_from_init(self):
        from src.python.fods import workbook_numeric_density as fn
        wb = parse_fods_strict(SAMPLES / "typed-values-basic.fods")
        result = fn(wb)
        assert isinstance(result, float)
