"""Tests for ODS sum_row function (rnext42)."""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import sum_row, OdsDocument, OdsSheet, OdsRow, OdsCell
from ods.ods_writer import document_to_ods_bytes


def _make_ods(rows: list[list]) -> str:
    """Create a minimal ODS file with given rows of numeric values."""
    ods_rows = []
    for row_vals in rows:
        cells = [
            OdsCell(value=float(v) if isinstance(v, (int, float)) else v,
                    value_type="float" if isinstance(v, (int, float)) else "string",
                    text=str(v))
            for v in row_vals
        ]
        ods_rows.append(OdsRow(cells=cells))
    doc = OdsDocument(
        sheets=[OdsSheet(name="Sheet1", rows=ods_rows)],
        path="",
    )
    ods_bytes = document_to_ods_bytes(doc)
    tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
    tmp.write(ods_bytes)
    tmp.close()
    return tmp.name


class TestSumRow:
    def test_numeric_row(self):
        path = _make_ods([[1.0, 2.0, 3.0]])
        try:
            result = sum_row(path, 0)
            assert abs(result - 6.0) < 1e-9
        finally:
            os.unlink(path)

    def test_out_of_bounds_row_returns_zero(self):
        # Row index beyond available rows returns 0.0
        path = _make_ods([[1.0]])
        try:
            result = sum_row(path, 999)
            assert result == 0.0
        finally:
            os.unlink(path)

    def test_out_of_range_row(self):
        path = _make_ods([[1.0]])
        try:
            result = sum_row(path, 99)
            assert result == 0.0
        finally:
            os.unlink(path)

    def test_returns_float(self):
        path = _make_ods([[5.0, 10.0]])
        try:
            result = sum_row(path, 0)
            assert isinstance(result, float)
        finally:
            os.unlink(path)
