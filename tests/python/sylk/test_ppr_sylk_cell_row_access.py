"""Tests for SYLK get_cell_value and get_row_values.

Sprint: product-progress-rnext
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

import pytest
from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    write_sylk,
    get_cell_value,
    get_row_values,
    SylkError,
)


def _make_doc(cells_spec: list[tuple]) -> SylkDocument:
    """Build a SylkDocument from (row, col, value, value_type) tuples."""
    cells = []
    for row, col, value, vtype in cells_spec:
        cells.append(SylkCell(row=row, col=col, value=value, value_type=vtype))
    rows = max((c.row for c in cells), default=0)
    cols = max((c.col for c in cells), default=0)
    return SylkDocument(cells=cells, rows=rows, cols=cols)


def _write_and_get(tmp_path, cells_spec):
    """Write a SYLK document and return the path."""
    doc = _make_doc(cells_spec)
    p = tmp_path / "test.slk"
    write_sylk(doc, p)
    return p


def test_get_cell_value_existing_numeric(tmp_path):
    """get_cell_value returns numeric value at given coords."""
    p = _write_and_get(tmp_path, [(1, 1, 42.0, "numeric"), (1, 2, 99.0, "numeric")])
    assert get_cell_value(p, 1, 1) == 42.0


def test_get_cell_value_existing_string(tmp_path):
    """get_cell_value returns string value."""
    p = _write_and_get(tmp_path, [(2, 3, "hello", "string")])
    assert get_cell_value(p, 2, 3) == "hello"


def test_get_cell_value_missing_returns_none(tmp_path):
    """get_cell_value returns None for empty/missing cell."""
    p = _write_and_get(tmp_path, [(1, 1, 10.0, "numeric")])
    assert get_cell_value(p, 5, 5) is None


def test_get_cell_value_out_of_range_returns_none(tmp_path):
    """get_cell_value returns None for out-of-range coordinates."""
    p = _write_and_get(tmp_path, [(1, 1, 1.0, "numeric")])
    assert get_cell_value(p, 100, 100) is None


def test_get_cell_value_different_row_col(tmp_path):
    """get_cell_value correctly distinguishes row/col combinations."""
    p = _write_and_get(tmp_path, [
        (1, 1, 10.0, "numeric"),
        (1, 2, 20.0, "numeric"),
        (2, 1, 30.0, "numeric"),
    ])
    assert get_cell_value(p, 1, 2) == 20.0
    assert get_cell_value(p, 2, 1) == 30.0


def test_get_row_values_single_row(tmp_path):
    """get_row_values returns values for a row."""
    p = _write_and_get(tmp_path, [
        (1, 1, "A", "string"),
        (1, 2, "B", "string"),
        (1, 3, "C", "string"),
    ])
    result = get_row_values(p, 1)
    assert result == ["A", "B", "C"]


def test_get_row_values_with_gaps(tmp_path):
    """get_row_values represents missing columns as None."""
    p = _write_and_get(tmp_path, [
        (1, 1, "A", "string"),
        (1, 3, "C", "string"),
    ])
    result = get_row_values(p, 1)
    assert result[0] == "A"
    assert result[1] is None
    assert result[2] == "C"


def test_get_row_values_missing_row_returns_empty(tmp_path):
    """get_row_values returns empty list for row with no cells."""
    p = _write_and_get(tmp_path, [(1, 1, 1.0, "numeric")])
    assert get_row_values(p, 99) == []


def test_get_row_values_returns_list(tmp_path):
    """get_row_values always returns a list type."""
    p = _write_and_get(tmp_path, [(2, 1, 5.0, "numeric")])
    result = get_row_values(p, 2)
    assert isinstance(result, list)


def test_get_cell_value_nonexistent_file():
    """get_cell_value raises SylkError for nonexistent file."""
    with pytest.raises(SylkError):
        get_cell_value("/nonexistent/path/file.slk", 1, 1)
