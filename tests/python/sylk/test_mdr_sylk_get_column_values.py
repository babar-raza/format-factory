"""Tests for sylk_parser.get_column_values — mainstream-product-deepening-rnext2.

Covers: normal column extraction, multi-row column, empty column, 1-based indexing,
non-existent column, sparse data with None gaps.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    write_sylk,
    get_column_values,
    SylkError,
)


def _make_sylk(cells: list[tuple[int, int, object, str]]) -> Path:
    """Build a temp SYLK file. Each cell: (row, col, value, value_type)."""
    tmp = tempfile.NamedTemporaryFile(suffix=".slk", delete=False)
    tmp.close()
    path = Path(tmp.name)
    doc_cells = [
        SylkCell(row=r, col=c, value=v, value_type=vt)
        for r, c, v, vt in cells
    ]
    max_row = max(c.row for c in doc_cells) if doc_cells else 0
    max_col = max(c.col for c in doc_cells) if doc_cells else 0
    doc = SylkDocument(cells=doc_cells, rows=max_row, cols=max_col)
    write_sylk(doc, path)
    return path


# ---------------------------------------------------------------------------
# Normal behavior
# ---------------------------------------------------------------------------

def test_get_column_values_single_value():
    path = _make_sylk([(1, 2, "hello", "string")])
    result = get_column_values(path, 2)
    assert result == ["hello"]


def test_get_column_values_multiple_rows():
    path = _make_sylk([(1, 1, "A", "string"), (2, 1, "B", "string"), (3, 1, "C", "string")])
    result = get_column_values(path, 1)
    assert result == ["A", "B", "C"]


def test_get_column_values_numeric():
    path = _make_sylk([(1, 3, 10, "numeric"), (2, 3, 20, "numeric"), (3, 3, 30, "numeric")])
    result = get_column_values(path, 3)
    assert result == [10, 20, 30]


def test_get_column_values_returns_only_target_column():
    # Two columns — only col 1 should be returned
    path = _make_sylk([
        (1, 1, "X", "string"), (1, 2, "Y", "string"),
        (2, 1, "A", "string"), (2, 2, "B", "string"),
    ])
    result = get_column_values(path, 1)
    assert result == ["X", "A"]


def test_get_column_values_col2_only():
    path = _make_sylk([
        (1, 1, "X", "string"), (1, 2, "Y", "string"),
        (2, 1, "A", "string"), (2, 2, "B", "string"),
    ])
    result = get_column_values(path, 2)
    assert result == ["Y", "B"]


# ---------------------------------------------------------------------------
# Boundary cases
# ---------------------------------------------------------------------------

def test_get_column_values_non_existent_column_returns_empty():
    path = _make_sylk([(1, 1, "hello", "string")])
    result = get_column_values(path, 5)
    assert result == []


def test_get_column_values_sparse_col_has_none_gaps():
    # Rows 1 and 3 have data in col 1 but row 2 does not
    path = _make_sylk([(1, 1, "first", "string"), (3, 1, "third", "string")])
    result = get_column_values(path, 1)
    assert result[0] == "first"
    assert result[1] is None  # gap
    assert result[2] == "third"
    assert len(result) == 3


def test_get_column_values_single_row_document():
    path = _make_sylk([(1, 1, 42, "numeric"), (1, 2, 99, "numeric")])
    result = get_column_values(path, 2)
    assert result == [99]


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------

def test_get_column_values_invalid_path_raises():
    with pytest.raises(SylkError):
        get_column_values("/nonexistent/does_not_exist.slk", 1)
