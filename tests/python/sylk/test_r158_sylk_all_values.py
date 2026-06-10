"""
test_r158_sylk_all_values.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT18-001
Added: 2026-06-10

Tests for SYLK get_all_values function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    get_all_values, write_sylk, SylkCell, SylkDocument, SylkError,
)


def _make_sylk(tmp_path: Path, cells: list[tuple[int, int, object, str]]) -> Path:
    doc = SylkDocument()
    for r, c, v, vt in cells:
        doc.cells.append(SylkCell(row=r, col=c, value=v, value_type=vt))
        doc.rows = max(doc.rows, r)
        doc.cols = max(doc.cols, c)
    p = tmp_path / "test.sylk"
    write_sylk(doc, p)
    return p


class TestGetAllValues:
    def test_single_cell(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 42.0, "numeric")])
        vals = get_all_values(src)
        assert vals == [42.0]

    def test_multiple_cells(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, 1.0, "numeric"),
            (1, 2, 2.0, "numeric"),
            (2, 1, 3.0, "numeric"),
        ])
        vals = get_all_values(src)
        assert vals == [1.0, 2.0, 3.0]

    def test_string_cells(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, "hello", "string"),
            (1, 2, "world", "string"),
        ])
        vals = get_all_values(src)
        assert vals == ["hello", "world"]

    def test_empty_document(self, tmp_path):
        src = _make_sylk(tmp_path, [])
        vals = get_all_values(src)
        assert vals == []

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(SylkError):
            get_all_values(tmp_path / "ghost.sylk")

    def test_returns_list(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 1.0, "numeric")])
        vals = get_all_values(src)
        assert isinstance(vals, list)
