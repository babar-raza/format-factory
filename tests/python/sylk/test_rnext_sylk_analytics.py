"""Product deepening tests for SYLK analytics functions.

Tests sylk_nonempty_rows, sylk_numeric_cell_count, sylk_string_cell_count,
sylk_max_column_index, sylk_row_count, sylk_empty_cell_count,
sylk_total_sum, sylk_column_count.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.sylk import (
    parse_sylk,
    sylk_nonempty_rows,
    sylk_numeric_cell_count,
    sylk_string_cell_count,
    sylk_max_column_index,
    sylk_row_count,
    sylk_empty_cell_count,
    sylk_total_sum,
    sylk_column_count,
)

# SYLK format: ID;P header, C;Y<row>;X<col>;K<value> for data, E for end
_SYLK_MINIMAL = """\
ID;P
C;Y1;X1;K"Name"
C;Y1;X2;K"Score"
C;Y2;X1;K"Alice"
C;Y2;X2;K42
C;Y3;X1;K"Bob"
C;Y3;X2;K87
E
"""

_SYLK_NUMERIC_ONLY = """\
ID;P
C;Y1;X1;K10
C;Y1;X2;K20
C;Y2;X1;K30
C;Y2;X2;K40
E
"""

_SYLK_EMPTY = """\
ID;P
E
"""


@pytest.fixture
def minimal_slk(tmp_path):
    f = tmp_path / "minimal.slk"
    f.write_text(_SYLK_MINIMAL, encoding="utf-8")
    return str(f)


@pytest.fixture
def numeric_slk(tmp_path):
    f = tmp_path / "numeric.slk"
    f.write_text(_SYLK_NUMERIC_ONLY, encoding="utf-8")
    return str(f)


@pytest.fixture
def empty_slk(tmp_path):
    f = tmp_path / "empty.slk"
    f.write_text(_SYLK_EMPTY, encoding="utf-8")
    return str(f)


class TestSylkRowMetrics:
    def test_nonempty_rows(self, minimal_slk):
        count = sylk_nonempty_rows(minimal_slk)
        assert count >= 2  # at least rows 1-3 have data

    def test_row_count(self, minimal_slk):
        count = sylk_row_count(minimal_slk)
        assert count >= 2

    def test_column_count(self, minimal_slk):
        count = sylk_column_count(minimal_slk)
        assert count >= 2

    def test_max_column_index(self, minimal_slk):
        idx = sylk_max_column_index(minimal_slk)
        assert idx >= 2  # columns 1 and 2

    def test_empty_file_zero_rows(self, empty_slk):
        assert sylk_row_count(empty_slk) == 0
        assert sylk_column_count(empty_slk) == 0


class TestSylkCellTypeCounts:
    def test_numeric_count(self, numeric_slk):
        count = sylk_numeric_cell_count(numeric_slk)
        assert count == 4  # four numeric cells

    def test_string_count(self, minimal_slk):
        count = sylk_string_cell_count(minimal_slk)
        assert count >= 2  # "Name", "Score", "Alice", "Bob"

    def test_empty_cell_count_zero_when_all_filled(self, numeric_slk):
        count = sylk_empty_cell_count(numeric_slk)
        assert count == 0


class TestSylkTotalSum:
    def test_numeric_only_sum(self, numeric_slk):
        total = sylk_total_sum(numeric_slk)
        assert total == pytest.approx(100.0)  # 10+20+30+40

    def test_mixed_sum_ignores_strings(self, minimal_slk):
        total = sylk_total_sum(minimal_slk)
        assert total == pytest.approx(129.0)  # 42+87

    def test_empty_sum_zero(self, empty_slk):
        assert sylk_total_sum(empty_slk) == pytest.approx(0.0)
