"""Tests for DIF count_distinct_values API.

Sprint: PRODUCT-API-BROADENING-20260612
Skill: /add-python-api
Format: DIF
API: count_distinct_values
"""

from __future__ import annotations

import os
import tempfile

import pytest

from src.python.dif.dif_parser import (
    count_distinct_values,
    write_dif,
    DifDocument,
    DifCell,
    DifError,
)


def _make_dif(rows_data, title="Test"):
    """Create a temp DIF file from row data (list of lists of values) and return path."""
    rows = []
    for row_vals in rows_data:
        cells = []
        for v in row_vals:
            if isinstance(v, (int, float)):
                cells.append(DifCell(value=v, value_type="numeric"))
            else:
                cells.append(DifCell(value=str(v), value_type="string"))
        rows.append(cells)
    ncols = max(len(r) for r in rows) if rows else 0
    doc = DifDocument(title=title, vectors=ncols, tuples=len(rows), rows=rows)
    fd, path = tempfile.mkstemp(suffix=".dif")
    os.close(fd)
    write_dif(doc, path)
    return path


def test_count_distinct_simple():
    """Three distinct string values in column 0."""
    path = _make_dif([["apple"], ["banana"], ["cherry"]])
    try:
        assert count_distinct_values(path, col=0) == 3
    finally:
        os.unlink(path)


def test_count_distinct_with_duplicates():
    """Column has duplicates — returns unique count only."""
    path = _make_dif([["a"], ["b"], ["a"], ["c"], ["b"]])
    try:
        assert count_distinct_values(path, col=0) == 3
    finally:
        os.unlink(path)


def test_count_distinct_numeric():
    """Distinct numeric values."""
    path = _make_dif([[10], [20], [10], [30]])
    try:
        assert count_distinct_values(path, col=0) == 3
    finally:
        os.unlink(path)


def test_count_distinct_multi_column():
    """Verify column isolation."""
    path = _make_dif([
        ["a", "x"],
        ["b", "x"],
        ["a", "y"],
    ])
    try:
        assert count_distinct_values(path, col=0) == 2
        assert count_distinct_values(path, col=1) == 2
    finally:
        os.unlink(path)


def test_count_distinct_all_same():
    """All cells have the same value — returns 1."""
    path = _make_dif([["x"], ["x"], ["x"]])
    try:
        assert count_distinct_values(path, col=0) == 1
    finally:
        os.unlink(path)


def test_count_distinct_single_value():
    """Single cell."""
    path = _make_dif([["only"]])
    try:
        assert count_distinct_values(path, col=0) == 1
    finally:
        os.unlink(path)


def test_count_distinct_out_of_range_column():
    """Out of range column returns 0."""
    path = _make_dif([["a"], ["b"]])
    try:
        assert count_distinct_values(path, col=99) == 0
    finally:
        os.unlink(path)


def test_count_distinct_invalid_file():
    """Non-DIF file raises DifError."""
    fd, path = tempfile.mkstemp(suffix=".dif")
    os.write(fd, b"not a dif file")
    os.close(fd)
    try:
        with pytest.raises(DifError):
            count_distinct_values(path, col=0)
    finally:
        os.unlink(path)
