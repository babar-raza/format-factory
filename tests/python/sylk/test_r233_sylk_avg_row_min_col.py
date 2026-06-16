"""Tests for sylk_avg_row_length and sylk_min_col_index (Sprint 23)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import sylk_avg_row_length, sylk_min_col_index

_SYLK_2X2 = """\
ID;P
C;Y1;X1;K"A"
C;Y1;X2;K"B"
C;Y2;X1;K10
C;Y2;X2;K20
E
"""

_SYLK_ONE_CELL = """\
ID;P
C;Y3;X2;K"hello"
E
"""

_SYLK_UNEVEN = """\
ID;P
C;Y1;X1;K"A"
C;Y1;X2;K"B"
C;Y1;X3;K"C"
C;Y2;X1;K1
E
"""


def _write(tmp_path, name, content):
    p = tmp_path / f"{name}.slk"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestSylkAvgRowLength:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt", _SYLK_2X2)
        result = sylk_avg_row_length(p)
        assert isinstance(result, float)

    def test_even_rows(self, tmp_path):
        p = _write(tmp_path, "er", _SYLK_2X2)
        result = sylk_avg_row_length(p)
        assert result == 2.0

    def test_uneven_rows(self, tmp_path):
        p = _write(tmp_path, "ur", _SYLK_UNEVEN)
        result = sylk_avg_row_length(p)
        assert result == 2.0  # (3+1)/2 rows

    def test_single_cell(self, tmp_path):
        p = _write(tmp_path, "sc", _SYLK_ONE_CELL)
        result = sylk_avg_row_length(p)
        assert result == 1.0

    def test_nonnegative(self, tmp_path):
        p = _write(tmp_path, "nn", _SYLK_2X2)
        assert sylk_avg_row_length(p) >= 0.0


class TestSylkMinColIndex:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt2", _SYLK_2X2)
        result = sylk_min_col_index(p)
        assert isinstance(result, int)

    def test_starts_at_col_1(self, tmp_path):
        p = _write(tmp_path, "c1", _SYLK_2X2)
        assert sylk_min_col_index(p) == 1

    def test_single_cell_col_2(self, tmp_path):
        p = _write(tmp_path, "sc2", _SYLK_ONE_CELL)
        assert sylk_min_col_index(p) == 2

    def test_positive(self, tmp_path):
        p = _write(tmp_path, "pos", _SYLK_2X2)
        assert sylk_min_col_index(p) >= 1

    def test_uneven_min_col(self, tmp_path):
        p = _write(tmp_path, "um", _SYLK_UNEVEN)
        assert sylk_min_col_index(p) == 1
