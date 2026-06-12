"""R169 — Gnumeric average_column exact-output hardening tests."""
from __future__ import annotations

import pytest
from src.python.gnumeric.gnumeric_codec import (
    average_column,
    create_gnumeric,
    min_column_value,
    max_column_value,
)


def _sheet(rows):
    return create_gnumeric([{"name": "Sheet1", "rows": rows}])


class TestAverageColumnExact:
    def test_average_1_2_3_is_2(self):
        m = _sheet([["1"], ["2"], ["3"]])
        assert average_column(m, 0, 0) == pytest.approx(2.0)

    def test_average_10_20_is_15(self):
        m = _sheet([["10"], ["20"]])
        assert average_column(m, 0, 0) == pytest.approx(15.0)

    def test_average_0_100_is_50(self):
        m = _sheet([["0"], ["100"]])
        assert average_column(m, 0, 0) == pytest.approx(50.0)

    def test_min_max_average_consistent(self):
        m = _sheet([["2"], ["4"], ["6"]])
        avg = average_column(m, 0, 0)
        mn = min_column_value(m, 0, 0)
        mx = max_column_value(m, 0, 0)
        assert mn <= avg <= mx

    def test_average_single_value_is_that_value(self):
        m = _sheet([["99"]])
        assert average_column(m, 0, 0) == pytest.approx(99.0)


class TestMinMaxColumnExact:
    def test_min_of_1_2_3_is_1(self):
        m = _sheet([["1"], ["2"], ["3"]])
        assert min_column_value(m, 0, 0) == pytest.approx(1.0)

    def test_max_of_1_2_3_is_3(self):
        m = _sheet([["1"], ["2"], ["3"]])
        assert max_column_value(m, 0, 0) == pytest.approx(3.0)

    def test_min_with_negatives(self):
        m = _sheet([["-5"], ["0"], ["5"]])
        assert min_column_value(m, 0, 0) == pytest.approx(-5.0)

    def test_max_with_negatives(self):
        m = _sheet([["-5"], ["0"], ["5"]])
        assert max_column_value(m, 0, 0) == pytest.approx(5.0)
