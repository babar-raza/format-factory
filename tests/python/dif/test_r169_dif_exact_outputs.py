"""R169 — DIF sum_column and average_column exact-output hardening tests."""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.dif.dif_parser import (
    DifCell,
    DifDocument,
    write_dif,
    sum_column,
    average_column,
    min_column_value,
    max_column_value,
)


def _file(rows, tmp_path):
    doc = DifDocument(title="exact")
    for r in rows:
        doc.rows.append([DifCell(value=v, value_type="numeric") for v in r])
    p = tmp_path / "exact.dif"
    write_dif(doc, p)
    return p


class TestSumColumnExact:
    def test_sum_1_2_3_is_6(self, tmp_path):
        p = _file([[1], [2], [3]], tmp_path)
        assert sum_column(p, 0) == pytest.approx(6.0)

    def test_sum_10_20_is_30(self, tmp_path):
        p = _file([[10], [20]], tmp_path)
        assert sum_column(p, 0) == pytest.approx(30.0)

    def test_sum_empty_is_zero(self, tmp_path):
        p = _file([], tmp_path)
        assert sum_column(p, 0) == 0.0

    def test_sum_col1_exact(self, tmp_path):
        p = _file([[1, 100], [2, 200], [3, 300]], tmp_path)
        assert sum_column(p, 1) == pytest.approx(600.0)


class TestAverageColumnExact:
    def test_avg_1_2_3_is_2(self, tmp_path):
        p = _file([[1], [2], [3]], tmp_path)
        assert average_column(p, 0) == pytest.approx(2.0)

    def test_avg_10_20_is_15(self, tmp_path):
        p = _file([[10], [20]], tmp_path)
        assert average_column(p, 0) == pytest.approx(15.0)

    def test_avg_empty_is_zero(self, tmp_path):
        p = _file([], tmp_path)
        assert average_column(p, 0) == 0.0

    def test_avg_single_is_that_value(self, tmp_path):
        p = _file([[77]], tmp_path)
        assert average_column(p, 0) == pytest.approx(77.0)

    def test_sum_avg_min_max_consistent(self, tmp_path):
        p = _file([[2], [4], [6]], tmp_path)
        avg = average_column(p, 0)
        mn = min_column_value(p, 0)
        mx = max_column_value(p, 0)
        assert mn <= avg <= mx
        assert sum_column(p, 0) == pytest.approx(3 * avg)
