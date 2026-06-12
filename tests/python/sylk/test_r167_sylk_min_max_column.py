"""Tests for SYLK min_column_value and max_column_value functions (rnext33)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    min_column_value,
    max_column_value,
    write_sylk,
    SylkDocument,
    SylkCell,
    SylkError,
)


def _make_sylk(tmp_path, cells):
    """Build a SYLK file from (row, col, value, value_type) tuples."""
    sylk_cells = [
        SylkCell(row=r, col=c, value=v, value_type=vt)
        for r, c, v, vt in cells
    ]
    doc = SylkDocument(cells=sylk_cells)
    p = tmp_path / "test.slk"
    write_sylk(doc, p)
    return p


class TestMinColumnValue:
    def test_basic_min(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, 10.0, "numeric"), (2, 1, 3.0, "numeric"), (3, 1, 7.0, "numeric")])
        assert min_column_value(p, 1) == 3.0

    def test_single_value(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, 42.0, "numeric")])
        assert min_column_value(p, 1) == 42.0

    def test_no_numeric_returns_none(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, "hello", "string"), (2, 1, "world", "string")])
        assert min_column_value(p, 1) is None

    def test_empty_column_returns_none(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 2, 5.0, "numeric")])  # col 2, not col 1
        assert min_column_value(p, 1) is None

    def test_negative_values(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, -5.0, "numeric"), (2, 1, -1.0, "numeric"), (3, 1, -10.0, "numeric")])
        assert min_column_value(p, 1) == -10.0

    def test_mixed_string_and_numeric(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, "header", "string"), (2, 1, 5.0, "numeric"), (3, 1, 2.0, "numeric")])
        assert min_column_value(p, 1) == 2.0

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(SylkError):
            min_column_value(tmp_path / "ghost.slk", 1)


class TestMaxColumnValue:
    def test_basic_max(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, 10.0, "numeric"), (2, 1, 3.0, "numeric"), (3, 1, 7.0, "numeric")])
        assert max_column_value(p, 1) == 10.0

    def test_single_value(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, 99.0, "numeric")])
        assert max_column_value(p, 1) == 99.0

    def test_no_numeric_returns_none(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, "hello", "string")])
        assert max_column_value(p, 1) is None

    def test_negative_values(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, -5.0, "numeric"), (2, 1, -1.0, "numeric"), (3, 1, -10.0, "numeric")])
        assert max_column_value(p, 1) == -1.0

    def test_mixed_string_and_numeric(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, "header", "string"), (2, 1, 5.0, "numeric"), (3, 1, 2.0, "numeric")])
        assert max_column_value(p, 1) == 5.0
