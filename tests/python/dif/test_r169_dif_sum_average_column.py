"""R169 — DIF sum_column and average_column tests."""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.dif.dif_parser import (
    DifCell,
    DifDocument,
    write_dif,
    sum_column,
    average_column,
)


def _make_dif(rows: list[list[tuple]], tmp_path: Path) -> Path:
    """Create a DIF file with given rows. Each cell is (value, type)."""
    doc = DifDocument(title="test")
    for row_data in rows:
        row = []
        for value, value_type in row_data:
            row.append(DifCell(value=value, value_type=value_type))
        doc.rows.append(row)
    out = tmp_path / "test.dif"
    write_dif(doc, out)
    return out


class TestSumColumn:
    def test_returns_float(self, tmp_path):
        path = _make_dif([[(1, "numeric")], [(2, "numeric")]], tmp_path)
        result = sum_column(path, 0)
        assert isinstance(result, float)

    def test_sum_three_values(self, tmp_path):
        path = _make_dif([[(1, "numeric")], [(2, "numeric")], [(3, "numeric")]], tmp_path)
        assert sum_column(path, 0) == pytest.approx(6.0)

    def test_sum_single_value(self, tmp_path):
        path = _make_dif([[(42, "numeric")]], tmp_path)
        assert sum_column(path, 0) == pytest.approx(42.0)

    def test_empty_file_returns_zero(self, tmp_path):
        path = _make_dif([], tmp_path)
        assert sum_column(path, 0) == 0.0

    def test_non_numeric_ignored(self, tmp_path):
        path = _make_dif(
            [[("label", "string")], [(5, "numeric")], [(3, "numeric")]],
            tmp_path,
        )
        assert sum_column(path, 0) == pytest.approx(8.0)

    def test_multi_column_targets_col1(self, tmp_path):
        path = _make_dif(
            [[(1, "numeric"), (10, "numeric")], [(2, "numeric"), (20, "numeric")]],
            tmp_path,
        )
        assert sum_column(path, 1) == pytest.approx(30.0)

    def test_out_of_range_col_returns_zero(self, tmp_path):
        path = _make_dif([[(1, "numeric")]], tmp_path)
        assert sum_column(path, 5) == 0.0


class TestAverageColumn:
    def test_returns_float(self, tmp_path):
        path = _make_dif([[(2, "numeric")], [(4, "numeric")]], tmp_path)
        result = average_column(path, 0)
        assert isinstance(result, float)

    def test_average_of_three(self, tmp_path):
        path = _make_dif([[(3, "numeric")], [(6, "numeric")], [(9, "numeric")]], tmp_path)
        assert average_column(path, 0) == pytest.approx(6.0)

    def test_average_of_two(self, tmp_path):
        path = _make_dif([[(10, "numeric")], [(20, "numeric")]], tmp_path)
        assert average_column(path, 0) == pytest.approx(15.0)

    def test_empty_returns_zero(self, tmp_path):
        path = _make_dif([], tmp_path)
        assert average_column(path, 0) == 0.0

    def test_all_non_numeric_returns_zero(self, tmp_path):
        path = _make_dif([[("a", "string")], [("b", "string")]], tmp_path)
        assert average_column(path, 0) == 0.0

    def test_exact_single_value(self, tmp_path):
        path = _make_dif([[(99, "numeric")]], tmp_path)
        assert average_column(path, 0) == pytest.approx(99.0)
