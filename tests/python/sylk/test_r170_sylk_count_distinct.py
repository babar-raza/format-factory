"""Tests for SYLK count_distinct_values API.

Sprint: PRODUCT-API-BROADENING-20260612
Skill: /add-python-api
Format: SYLK
API: count_distinct_values
"""

from __future__ import annotations

import os
import tempfile

import pytest

from src.python.sylk.sylk_parser import (
    count_distinct_values,
    write_sylk,
    SylkDocument,
    SylkCell,
    SylkError,
)


def _make_sylk(cells, rows, cols):
    """Create a temp SYLK file and return path."""
    doc = SylkDocument(cells=cells, rows=rows, cols=cols)
    fd, path = tempfile.mkstemp(suffix=".sylk")
    os.close(fd)
    write_sylk(doc, path)
    return path


def test_count_distinct_simple():
    """Three distinct string values in column 1."""
    cells = [
        SylkCell(row=1, col=1, value="apple", value_type="string"),
        SylkCell(row=2, col=1, value="banana", value_type="string"),
        SylkCell(row=3, col=1, value="cherry", value_type="string"),
    ]
    path = _make_sylk(cells, 3, 1)
    try:
        assert count_distinct_values(path, col=1) == 3
    finally:
        os.unlink(path)


def test_count_distinct_with_duplicates():
    """Column has duplicates — returns unique count only."""
    cells = [
        SylkCell(row=1, col=1, value="a", value_type="string"),
        SylkCell(row=2, col=1, value="b", value_type="string"),
        SylkCell(row=3, col=1, value="a", value_type="string"),
        SylkCell(row=4, col=1, value="c", value_type="string"),
        SylkCell(row=5, col=1, value="b", value_type="string"),
    ]
    path = _make_sylk(cells, 5, 1)
    try:
        assert count_distinct_values(path, col=1) == 3
    finally:
        os.unlink(path)


def test_count_distinct_numeric():
    """Distinct numeric values."""
    cells = [
        SylkCell(row=1, col=1, value=10, value_type="numeric"),
        SylkCell(row=2, col=1, value=20, value_type="numeric"),
        SylkCell(row=3, col=1, value=10, value_type="numeric"),
        SylkCell(row=4, col=1, value=30, value_type="numeric"),
    ]
    path = _make_sylk(cells, 4, 1)
    try:
        assert count_distinct_values(path, col=1) == 3
    finally:
        os.unlink(path)


def test_count_distinct_multi_column():
    """Verify column isolation."""
    cells = [
        SylkCell(row=1, col=1, value="a", value_type="string"),
        SylkCell(row=1, col=2, value="x", value_type="string"),
        SylkCell(row=2, col=1, value="b", value_type="string"),
        SylkCell(row=2, col=2, value="x", value_type="string"),
        SylkCell(row=3, col=1, value="a", value_type="string"),
        SylkCell(row=3, col=2, value="y", value_type="string"),
    ]
    path = _make_sylk(cells, 3, 2)
    try:
        assert count_distinct_values(path, col=1) == 2
        assert count_distinct_values(path, col=2) == 2
    finally:
        os.unlink(path)


def test_count_distinct_all_same():
    """All cells have the same value — returns 1."""
    cells = [
        SylkCell(row=1, col=1, value="x", value_type="string"),
        SylkCell(row=2, col=1, value="x", value_type="string"),
        SylkCell(row=3, col=1, value="x", value_type="string"),
    ]
    path = _make_sylk(cells, 3, 1)
    try:
        assert count_distinct_values(path, col=1) == 1
    finally:
        os.unlink(path)


def test_count_distinct_empty_column():
    """Column with no cells — returns 0."""
    cells = [
        SylkCell(row=1, col=1, value="a", value_type="string"),
    ]
    path = _make_sylk(cells, 1, 2)
    try:
        assert count_distinct_values(path, col=2) == 0
    finally:
        os.unlink(path)


def test_count_distinct_single_value():
    """Single cell in column."""
    cells = [
        SylkCell(row=1, col=1, value="only", value_type="string"),
    ]
    path = _make_sylk(cells, 1, 1)
    try:
        assert count_distinct_values(path, col=1) == 1
    finally:
        os.unlink(path)


def test_count_distinct_invalid_file():
    """Non-SYLK file raises SylkError."""
    fd, path = tempfile.mkstemp(suffix=".sylk")
    os.write(fd, b"not a sylk file")
    os.close(fd)
    try:
        with pytest.raises(SylkError):
            count_distinct_values(path, col=1)
    finally:
        os.unlink(path)
