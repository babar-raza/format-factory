"""Tests for ODS count_nonempty_cells function (rnext36)."""
from __future__ import annotations

import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import count_nonempty_cells, OdsInvalidContainerError
from ods.ods_writer import write_ods
from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell


def _make_ods(rows_data: list[list]) -> str:
    """Create a temp ODS with given rows."""
    cells_by_row = []
    for row_vals in rows_data:
        cells = []
        for val in row_vals:
            vt = "float" if isinstance(val, (int, float)) and not isinstance(val, bool) else "string"
            cells.append(OdsCell(value=val, value_type=vt, text=str(val) if val is not None else ""))
        cells_by_row.append(OdsRow(cells=cells))
    sheet = OdsSheet(name="Sheet1", rows=cells_by_row)
    doc = OdsDocument(sheets=[sheet])
    tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
    tmp.close()
    write_ods(doc, tmp.name)
    return tmp.name


class TestCountNonemptyCells:
    def test_basic_count(self):
        path = _make_ods([["A", "B"], ["C", None]])
        try:
            assert count_nonempty_cells(path) == 3
        finally:
            os.unlink(path)

    def test_all_filled(self):
        path = _make_ods([[1, 2], [3, 4]])
        try:
            assert count_nonempty_cells(path) == 4
        finally:
            os.unlink(path)

    def test_empty_sheet(self):
        path = _make_ods([])
        try:
            assert count_nonempty_cells(path) == 0
        finally:
            os.unlink(path)

    def test_bad_sheet_index(self):
        path = _make_ods([[1, 2]])
        try:
            assert count_nonempty_cells(path, sheet_index=5) == 0
        finally:
            os.unlink(path)

    def test_nonexistent_file(self):
        import pytest
        with pytest.raises(Exception):
            count_nonempty_cells("/nonexistent/file.ods")
