"""Tests for SYLK average_column function (rnext41)."""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import average_column, write_sylk, parse_sylk_strict, SylkDocument, SylkCell


def _make_sylk(cells: list[tuple[int, int, object]]) -> str:
    """Create a SYLK file with given (row, col, value) cells."""
    doc = SylkDocument(
        cells=[SylkCell(row=r, col=c, value=v) for r, c, v in cells],
        rows=max(r for r, c, v in cells) if cells else 0,
        cols=max(c for r, c, v in cells) if cells else 0,
    )
    tmp = tempfile.NamedTemporaryFile(suffix=".slk", delete=False)
    tmp.close()
    write_sylk(doc, tmp.name)
    return tmp.name


class TestAverageColumn:
    def test_numeric_column(self):
        path = _make_sylk([(1, 1, 10.0), (2, 1, 20.0), (3, 1, 30.0)])
        try:
            result = average_column(path, 1)
            assert abs(result - 20.0) < 1e-9
        finally:
            os.unlink(path)

    def test_empty_column_returns_zero(self):
        path = _make_sylk([(1, 2, 5.0)])  # col 1 has no values
        try:
            result = average_column(path, 1)
            assert result == 0.0
        finally:
            os.unlink(path)

    def test_single_value(self):
        path = _make_sylk([(1, 1, 42.0)])
        try:
            result = average_column(path, 1)
            assert abs(result - 42.0) < 1e-9
        finally:
            os.unlink(path)

    def test_returns_float(self):
        path = _make_sylk([(1, 1, 5.0), (2, 1, 7.0)])
        try:
            result = average_column(path, 1)
            assert isinstance(result, float)
        finally:
            os.unlink(path)

    def test_uses_numeric_row_fixture(self):
        fixture = str(_REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk")
        # numeric-row.slk has cells: (1,1,1), (1,2,2), (1,3,3)
        # col 1: [1] → avg = 1.0
        result = average_column(fixture, 1)
        assert isinstance(result, float)
        assert result >= 0.0
