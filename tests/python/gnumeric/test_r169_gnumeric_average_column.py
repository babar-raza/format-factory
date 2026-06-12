"""R169 — Gnumeric average_column tests."""
from __future__ import annotations

import pytest
from src.python.gnumeric.gnumeric_codec import (
    average_column,
    create_gnumeric,
    get_sheet_count,
)


def _make_model(rows: list[list[str]]) -> dict:
    """Build a minimal Gnumeric model with one sheet."""
    return create_gnumeric([{"name": "Sheet1", "rows": rows}])


class TestAverageColumnBasic:
    def test_returns_float(self):
        model = _make_model([["1"], ["2"], ["3"]])
        result = average_column(model, 0, 0)
        assert isinstance(result, float)

    def test_average_of_three(self):
        model = _make_model([["2"], ["4"], ["6"]])
        result = average_column(model, 0, 0)
        assert result == pytest.approx(4.0)

    def test_average_of_two(self):
        model = _make_model([["10"], ["20"]])
        result = average_column(model, 0, 0)
        assert result == pytest.approx(15.0)

    def test_single_value(self):
        model = _make_model([["7"]])
        result = average_column(model, 0, 0)
        assert result == pytest.approx(7.0)

    def test_empty_column_returns_zero(self):
        model = _make_model([])
        result = average_column(model, 0, 0)
        assert result == 0.0

    def test_non_numeric_ignored(self):
        model = _make_model([["hello"], ["4"], ["6"]])
        result = average_column(model, 0, 0)
        assert result == pytest.approx(5.0)

    def test_all_non_numeric_returns_zero(self):
        model = _make_model([["abc"], ["def"]])
        result = average_column(model, 0, 0)
        assert result == 0.0


class TestAverageColumnExact:
    def test_five_values_exact(self):
        model = _make_model([["1"], ["2"], ["3"], ["4"], ["5"]])
        result = average_column(model, 0, 0)
        assert result == pytest.approx(3.0)

    def test_mixed_integers_exact(self):
        model = _make_model([["10"], ["20"], ["30"]])
        result = average_column(model, 0, 0)
        assert result == pytest.approx(20.0)
