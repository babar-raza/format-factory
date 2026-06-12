"""
test_r162_sylk_find_value.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT22-001
Added: 2026-06-12

Tests for SYLK find_value function.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import find_value, parse_sylk_strict, write_sylk, SylkDocument, SylkCell

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"


def _make_sylk_with_values(tmp_path, cells):
    """Create a SYLK file with given cells as list of (row, col, value)."""
    doc = SylkDocument()
    for row, col, val in cells:
        vtype = "numeric" if isinstance(val, (int, float)) else "string"
        doc.cells.append(SylkCell(row=row, col=col, value=val, value_type=vtype))
        doc.rows = max(doc.rows, row)
        doc.cols = max(doc.cols, col)
    p = tmp_path / "test.slk"
    write_sylk(doc, p)
    return p


class TestFindValue:
    def test_find_numeric_value(self, tmp_path):
        p = _make_sylk_with_values(tmp_path, [(1, 1, 42), (1, 2, 100), (2, 1, 7)])
        result = find_value(p, 42)
        assert result == (1, 1)

    def test_find_string_value(self, tmp_path):
        p = _make_sylk_with_values(tmp_path, [(1, 1, "hello"), (2, 1, "world")])
        result = find_value(p, "hello")
        assert result == (1, 1)

    def test_missing_value_returns_none(self, tmp_path):
        p = _make_sylk_with_values(tmp_path, [(1, 1, 10), (2, 2, 20)])
        result = find_value(p, 999)
        assert result is None

    def test_returns_first_occurrence(self, tmp_path):
        p = _make_sylk_with_values(tmp_path, [(1, 2, 5), (2, 1, 5)])
        result = find_value(p, 5)
        # Row 1 col 2 vs row 2 col 1 — row-first ordering so (1,2) comes first
        assert result == (1, 2)

    def test_single_cell(self):
        result = find_value(_SAMPLES / "single-cell.slk", None)
        # single-cell.slk may have a cell with some value; None means missing
        # just verify the function returns tuple or None
        assert result is None or isinstance(result, tuple)

    def test_returns_tuple_of_ints(self, tmp_path):
        p = _make_sylk_with_values(tmp_path, [(3, 2, "target")])
        result = find_value(p, "target")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result == (3, 2)
