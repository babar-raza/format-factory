"""
test_r157_sylk_cell_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT16-001
Added: 2026-06-10

Tests for SYLK get_cell_count function.
Authority: P5 (SAL-SYLK-00001)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    get_cell_count,
    write_sylk,
    SylkCell,
    SylkDocument,
    SylkError,
)


def _make_sylk(tmp_path: Path, cells: list[tuple[int, int, object, str]]) -> Path:
    """Create a SYLK file. Each tuple is (row, col, value, value_type)."""
    doc = SylkDocument()
    for r, c, v, vt in cells:
        doc.cells.append(SylkCell(row=r, col=c, value=v, value_type=vt))
        doc.rows = max(doc.rows, r)
        doc.cols = max(doc.cols, c)
    p = tmp_path / "test.sylk"
    write_sylk(doc, p)
    return p


class TestGetCellCount:
    def test_single_cell(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 42.0, "numeric")])
        assert get_cell_count(src) == 1

    def test_multiple_cells(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, 1.0, "numeric"),
            (1, 2, 2.0, "numeric"),
            (2, 1, 3.0, "numeric"),
        ])
        assert get_cell_count(src) == 3

    def test_empty_document(self, tmp_path):
        src = _make_sylk(tmp_path, [])
        assert get_cell_count(src) == 0

    def test_string_cells(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, "hello", "string"),
            (1, 2, "world", "string"),
        ])
        assert get_cell_count(src) == 2

    def test_mixed_types(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, "Name", "string"),
            (1, 2, 100.0, "numeric"),
            (2, 1, "Age", "string"),
            (2, 2, 25.0, "numeric"),
        ])
        assert get_cell_count(src) == 4

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(SylkError):
            get_cell_count(tmp_path / "ghost.sylk")

    def test_none_values_excluded(self, tmp_path):
        doc = SylkDocument()
        doc.cells.append(SylkCell(row=1, col=1, value=None, value_type="string"))
        doc.cells.append(SylkCell(row=1, col=2, value=42.0, value_type="numeric"))
        doc.rows = 1
        doc.cols = 2
        p = tmp_path / "test.sylk"
        write_sylk(doc, p)
        assert get_cell_count(p) == 1

    def test_sparse_grid(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, 1.0, "numeric"),
            (5, 5, 2.0, "numeric"),
            (10, 10, 3.0, "numeric"),
        ])
        assert get_cell_count(src) == 3
