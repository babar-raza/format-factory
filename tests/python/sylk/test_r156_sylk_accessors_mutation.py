"""
test_r156_sylk_accessors_mutation.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT14-001
Added: 2026-06-10

Tests for SYLK get_row_count, get_column_count, set_cell_value functions.
Authority: P5 (FACT-SYLK-001)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    get_row_count,
    get_column_count,
    set_cell_value,
    get_cell_value,
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


# ---- get_row_count tests ----


class TestGetRowCount:
    def test_single_cell(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 42, "numeric")])
        assert get_row_count(src) == 1

    def test_multiple_rows(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, "a", "string"),
            (3, 1, "b", "string"),
        ])
        assert get_row_count(src) == 3

    def test_empty_document(self, tmp_path):
        src = _make_sylk(tmp_path, [])
        assert get_row_count(src) == 0

    def test_large_row_index(self, tmp_path):
        src = _make_sylk(tmp_path, [(100, 1, 1, "numeric")])
        assert get_row_count(src) == 100

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(SylkError):
            get_row_count(tmp_path / "ghost.sylk")


# ---- get_column_count tests ----


class TestGetColumnCount:
    def test_single_cell(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 42, "numeric")])
        assert get_column_count(src) == 1

    def test_multiple_columns(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, "a", "string"),
            (1, 5, "b", "string"),
        ])
        assert get_column_count(src) == 5

    def test_empty_document(self, tmp_path):
        src = _make_sylk(tmp_path, [])
        assert get_column_count(src) == 0

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(SylkError):
            get_column_count(tmp_path / "ghost.sylk")


# ---- set_cell_value tests ----


class TestSetCellValue:
    def test_update_existing_cell(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 10, "numeric")])
        dst = tmp_path / "out.sylk"
        result = set_cell_value(src, dst, 1, 1, 99, "numeric")
        assert result["ok"] is True
        assert result["old_value"] == 10
        assert result["new_value"] == 99
        assert get_cell_value(dst, 1, 1) == 99

    def test_add_new_cell(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 10, "numeric")])
        dst = tmp_path / "out.sylk"
        result = set_cell_value(src, dst, 2, 2, "hello", "string")
        assert result["ok"] is True
        assert result["old_value"] is None
        assert get_cell_value(dst, 2, 2) == "hello"

    def test_preserves_other_cells(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, 10, "numeric"),
            (1, 2, 20, "numeric"),
        ])
        dst = tmp_path / "out.sylk"
        set_cell_value(src, dst, 1, 1, 99, "numeric")
        assert get_cell_value(dst, 1, 2) == 20

    def test_string_value(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "old", "string")])
        dst = tmp_path / "out.sylk"
        set_cell_value(src, dst, 1, 1, "new", "string")
        assert get_cell_value(dst, 1, 1) == "new"

    def test_invalid_row_zero(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 10, "numeric")])
        dst = tmp_path / "out.sylk"
        with pytest.raises(SylkError):
            set_cell_value(src, dst, 0, 1, 1, "numeric")

    def test_invalid_col_zero(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 10, "numeric")])
        dst = tmp_path / "out.sylk"
        with pytest.raises(SylkError):
            set_cell_value(src, dst, 1, 0, 1, "numeric")

    def test_updates_dimensions(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 10, "numeric")])
        dst = tmp_path / "out.sylk"
        set_cell_value(src, dst, 5, 3, 42, "numeric")
        assert get_row_count(dst) == 5
        assert get_column_count(dst) == 3

    def test_result_keys(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 10, "numeric")])
        dst = tmp_path / "out.sylk"
        result = set_cell_value(src, dst, 1, 1, 20, "numeric")
        assert "ok" in result
        assert "row" in result
        assert "col" in result
        assert "old_value" in result
        assert "new_value" in result

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(SylkError):
            set_cell_value(tmp_path / "ghost.sylk", tmp_path / "out.sylk", 1, 1, 1, "numeric")
