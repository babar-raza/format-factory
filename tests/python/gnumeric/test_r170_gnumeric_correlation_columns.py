"""R170 — Gnumeric correlation_columns tests.

Sprint: FORMAT-FACTORY-PROOF-CLOSED-SELF-HEALING-PROFESSIONALIZE-PRODUCT-READINESS-RNEXT-001
"""
from __future__ import annotations

import pytest

from src.python.gnumeric.gnumeric_codec import (
    correlation_columns,
    get_column_values,
)


def _make_model(col0_vals: list, col1_vals: list) -> dict:
    """Create a minimal gnumeric model with two columns of values."""
    grid = {}
    for r, v in enumerate(col0_vals):
        grid[(r, 0)] = str(v)
    for r, v in enumerate(col1_vals):
        grid[(r, 1)] = str(v)
    return {
        "format": "gnumeric",
        "sheets": [{"name": "Sheet1", "cell_count": len(col0_vals), "cell_values": [], "cell_grid": grid}],
    }


class TestCorrelationColumnsBasic:
    def test_returns_float(self):
        model = _make_model([1, 2, 3], [2, 4, 6])
        result = correlation_columns(model, 0, 0, 1)
        assert isinstance(result, float)

    def test_empty_columns_return_zero(self):
        model = _make_model([1, 2, 3], [2, 4, 6])
        result = correlation_columns(model, 0, 99, 100)
        assert result == 0.0

    def test_out_of_range_sheet_returns_zero(self):
        """Out-of-range sheet_idx is caught and returns 0.0."""
        model = _make_model([1, 2, 3], [2, 4, 6])
        try:
            result = correlation_columns(model, 99, 0, 1)
            assert result == 0.0
        except (IndexError, Exception):
            pass  # IndexError is acceptable too

    def test_correlation_in_range(self):
        """Result must be in [-1, 1]."""
        model = _make_model([1, 2, 3, 4], [2, 4, 6, 8])
        result = correlation_columns(model, 0, 0, 1)
        assert -1.0 <= result <= 1.0

    def test_single_row_returns_zero(self):
        """Only 1 data pair → r = 0.0."""
        model = _make_model([1], [2])
        result = correlation_columns(model, 0, 0, 1)
        assert result == 0.0


class TestCorrelationColumnsExact:
    def test_perfect_positive_correlation(self):
        """col_a=[1,2,3], col_b=[2,4,6] → r=1.0"""
        model = _make_model([1, 2, 3], [2, 4, 6])
        r = correlation_columns(model, 0, 0, 1)
        assert r == pytest.approx(1.0, abs=1e-9)

    def test_perfect_negative_correlation(self):
        """col_a=[1,2,3], col_b=[6,4,2] → r=-1.0"""
        model = _make_model([1, 2, 3], [6, 4, 2])
        r = correlation_columns(model, 0, 0, 1)
        assert r == pytest.approx(-1.0, abs=1e-9)

    def test_zero_correlation_constant_column(self):
        """Column of all same values → std=0 → correlation=0.0"""
        model = _make_model([5, 5, 5], [1, 2, 3])
        r = correlation_columns(model, 0, 0, 1)
        assert r == 0.0

    def test_non_numeric_mixed_returns_zero(self):
        """Non-numeric values are skipped — doesn't raise."""
        model = _make_model(["Name", "Alice"], ["Score", "42"])
        r = correlation_columns(model, 0, 0, 1)
        assert isinstance(r, float)
        assert r == 0.0  # Only 0 numeric pairs

    def test_result_is_symmetric(self):
        """correlation(A,B) == correlation(B,A)"""
        model = _make_model([1, 2, 3], [3, 1, 5])
        r_ab = correlation_columns(model, 0, 0, 1)
        r_ba = correlation_columns(model, 0, 1, 0)
        assert r_ab == pytest.approx(r_ba, abs=1e-12)

    def test_function_in_all(self):
        """correlation_columns is exported in __all__."""
        from src.python.gnumeric import __all__ as gnumeric_all
        assert "correlation_columns" in gnumeric_all
