"""
test_r160_sylk_nonempty_sum.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT20-001
Added: 2026-06-10

Tests for SYLK count_nonempty_cells and sum_column functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    count_nonempty_cells,
    sum_column,
    parse_sylk_strict,
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
    p = tmp_path / "test.sylk"
    write_sylk(doc, p)
    return p


class TestCountNonemptyCells:
    def test_all_nonempty(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, 10.0, "numeric"), (1, 2, "hello", "string")])
        assert count_nonempty_cells(p) == 2

    def test_with_none(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, 10.0, "numeric"), (1, 2, None, "string")])
        assert count_nonempty_cells(p) == 1

    def test_with_empty_string(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, "", "string"), (1, 2, "val", "string")])
        assert count_nonempty_cells(p) == 1

    def test_empty_document(self, tmp_path):
        p = _make_sylk(tmp_path, [])
        assert count_nonempty_cells(p) == 0

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(SylkError):
            count_nonempty_cells(tmp_path / "ghost.sylk")


class TestSumColumn:
    def test_numeric_column(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, 10.0, "numeric"), (2, 1, 20.0, "numeric"), (3, 1, 30.0, "numeric")])
        assert sum_column(p, 1) == 60.0

    def test_mixed_column(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, 10.0, "numeric"), (2, 1, "text", "string"), (3, 1, 5.0, "numeric")])
        assert sum_column(p, 1) == 15.0

    def test_no_numeric(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, "a", "string"), (2, 1, "b", "string")])
        assert sum_column(p, 1) == 0.0

    def test_wrong_column(self, tmp_path):
        p = _make_sylk(tmp_path, [(1, 1, 10.0, "numeric"), (2, 1, 20.0, "numeric")])
        assert sum_column(p, 2) == 0.0

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(SylkError):
            sum_column(tmp_path / "ghost.sylk", 1)
