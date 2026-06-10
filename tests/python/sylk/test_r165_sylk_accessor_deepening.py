"""
test_r165_sylk_accessor_deepening.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT30-001
Added: 2026-06-10

Deepening tests for SYLK functions with thin coverage:
- count_nonempty_cells (was 1 test)
- sum_column (was 3 tests)
- sylk_to_html (was 2 tests)
- add_row edge cases (was 2 tests)
- delete_row edge cases (was 2 tests)
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
    sylk_to_html,
    add_row,
    delete_row,
    write_sylk,
    parse_sylk_strict,
    SylkCell,
    SylkDocument,
    SylkError,
)


def _make_sylk(tmp_path: Path, cells: list[tuple[int, int, object, str]], name="test.sylk") -> Path:
    doc = SylkDocument()
    for r, c, v, vt in cells:
        doc.cells.append(SylkCell(row=r, col=c, value=v, value_type=vt))
        doc.rows = max(doc.rows, r)
        doc.cols = max(doc.cols, c)
    p = tmp_path / name
    write_sylk(doc, p)
    return p


# ── count_nonempty_cells deepening ──────────────────────────────────────

class TestCountNonemptyCellsDeepening:

    def test_all_nonempty(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, 10.0, "numeric"),
            (1, 2, "hello", "string"),
            (2, 1, 20.0, "numeric"),
        ])
        assert count_nonempty_cells(src) == 3

    def test_empty_document(self, tmp_path):
        src = _make_sylk(tmp_path, [])
        assert count_nonempty_cells(src) == 0

    def test_nonexistent_raises(self, tmp_path):
        with pytest.raises(SylkError):
            count_nonempty_cells(tmp_path / "ghost.sylk")

    def test_single_cell(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "value", "string")])
        assert count_nonempty_cells(src) == 1


# ── sum_column deepening ────────────────────────────────────────────────

class TestSumColumnDeepening:

    def test_mixed_types(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, 10.0, "numeric"),
            (2, 1, "text", "string"),
            (3, 1, 30.0, "numeric"),
        ])
        assert sum_column(src, 1) == 40.0

    def test_empty_column(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "text", "string")])
        assert sum_column(src, 2) == 0.0

    def test_single_value(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, 42.0, "numeric")])
        assert sum_column(src, 1) == 42.0

    def test_empty_document(self, tmp_path):
        src = _make_sylk(tmp_path, [])
        assert sum_column(src, 1) == 0.0


# ── sylk_to_html deepening ──────────────────────────────────────────────

class TestSylkToHtmlDeepening:

    def test_returns_string(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "data", "string")])
        result = sylk_to_html(src)
        assert isinstance(result, str)

    def test_contains_table_tag(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "data", "string")])
        result = sylk_to_html(src)
        assert "<table" in result
        assert "</table>" in result

    def test_contains_cell_value(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "hello", "string")])
        result = sylk_to_html(src)
        assert "hello" in result

    def test_empty_document(self, tmp_path):
        src = _make_sylk(tmp_path, [])
        result = sylk_to_html(src)
        assert "<table" in result

    def test_multiple_cells(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, "A1", "string"),
            (1, 2, "B1", "string"),
            (2, 1, "A2", "string"),
        ])
        result = sylk_to_html(src)
        assert "A1" in result
        assert "B1" in result
        assert "A2" in result

    def test_html_escaping(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "<b>bold</b>", "string")])
        result = sylk_to_html(src)
        assert "&lt;b&gt;" in result


# ── add_row deepening ───────────────────────────────────────────────────

class TestAddRowDeepening:

    def test_add_to_empty(self, tmp_path):
        src = _make_sylk(tmp_path, [], name="src.sylk")
        dest = tmp_path / "dest.sylk"
        result = add_row(src, dest, [1.0, "text"])
        assert result["success"] is True

    def test_add_preserves_existing(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "orig", "string")], name="src.sylk")
        dest = tmp_path / "dest.sylk"
        add_row(src, dest, [99.0])
        doc = parse_sylk_strict(dest)
        values = [c.value for c in doc.cells]
        assert "orig" in values
        assert 99.0 in values

    def test_returns_row_index(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "a", "string")], name="src.sylk")
        dest = tmp_path / "dest.sylk"
        result = add_row(src, dest, ["b"])
        assert "row_index" in result


# ── delete_row deepening ────────────────────────────────────────────────

class TestDeleteRowDeepening:

    def test_delete_only_row(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "gone", "string")], name="src.sylk")
        dest = tmp_path / "dest.sylk"
        result = delete_row(src, dest, 1)
        assert result["success"] is True
        assert result["deleted_count"] == 1

    def test_delete_preserves_other_rows(self, tmp_path):
        src = _make_sylk(tmp_path, [
            (1, 1, "row1", "string"),
            (2, 1, "row2", "string"),
            (3, 1, "row3", "string"),
        ], name="src.sylk")
        dest = tmp_path / "dest.sylk"
        delete_row(src, dest, 2)
        doc = parse_sylk_strict(dest)
        values = [c.value for c in doc.cells]
        assert "row1" in values
        assert "row3" in values
        assert "row2" not in values

    def test_delete_nonexistent_row(self, tmp_path):
        src = _make_sylk(tmp_path, [(1, 1, "data", "string")], name="src.sylk")
        dest = tmp_path / "dest.sylk"
        result = delete_row(src, dest, 99)
        assert result["deleted_count"] == 0
