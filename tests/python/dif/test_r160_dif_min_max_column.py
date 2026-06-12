"""
test_r160_dif_min_max_column.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT20-001
Added: 2026-06-10

Tests for DIF min_column_value and max_column_value functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    min_column_value,
    max_column_value,
    write_dif,
    DifDocument,
    DifCell,
    DifError,
)

_SAMPLES = _REPO / "samples" / "by-format" / "dif" / "valid"


def _make_dif(tmp_path, rows):
    """Build a DIF file from a list of lists of values."""
    doc_rows = []
    for row_vals in rows:
        cells = []
        for v in row_vals:
            vtype = "numeric" if isinstance(v, (int, float)) else "string"
            cells.append(DifCell(value=v, value_type=vtype))
        doc_rows.append(cells)
    ncols = max(len(r) for r in rows) if rows else 0
    doc = DifDocument(
        title="test",
        vectors=ncols,
        tuples=len(rows),
        rows=doc_rows,
    )
    p = tmp_path / "test.dif"
    write_dif(doc, p)
    return p


class TestMinColumnValue:
    def test_single_column(self, tmp_path):
        p = _make_dif(tmp_path, [[10.0], [5.0], [20.0]])
        assert min_column_value(p, 0) == 5.0

    def test_mixed_types(self, tmp_path):
        p = _make_dif(tmp_path, [[10.0], ["hello"], [3.0]])
        assert min_column_value(p, 0) == 3.0

    def test_no_numeric(self, tmp_path):
        p = _make_dif(tmp_path, [["a"], ["b"]])
        assert min_column_value(p, 0) is None

    def test_out_of_range_col(self, tmp_path):
        p = _make_dif(tmp_path, [[1.0]])
        assert min_column_value(p, 5) is None

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(DifError):
            min_column_value(tmp_path / "ghost.dif", 0)


class TestMaxColumnValue:
    def test_single_column(self, tmp_path):
        p = _make_dif(tmp_path, [[10.0], [5.0], [20.0]])
        assert max_column_value(p, 0) == 20.0

    def test_mixed_types(self, tmp_path):
        p = _make_dif(tmp_path, [[10.0], ["hello"], [3.0]])
        assert max_column_value(p, 0) == 10.0

    def test_no_numeric(self, tmp_path):
        p = _make_dif(tmp_path, [["a"], ["b"]])
        assert max_column_value(p, 0) is None

    def test_multiple_columns(self, tmp_path):
        p = _make_dif(tmp_path, [[1.0, 100.0], [2.0, 50.0]])
        assert max_column_value(p, 0) == 2.0
        assert max_column_value(p, 1) == 100.0

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(DifError):
            max_column_value(tmp_path / "ghost.dif", 0)
