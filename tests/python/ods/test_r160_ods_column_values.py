"""Tests for ODS get_column_values.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT21-001
Covers: column value extraction from ODS files
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell, get_column_values
from ods.ods_writer import write_ods


def _make_ods(rows_data):
    """Create a temp ODS file from row data (list of lists)."""
    rows = []
    for row_vals in rows_data:
        cells = []
        for val in row_vals:
            vtype = "float" if isinstance(val, (int, float)) else "string"
            cells.append(OdsCell(value=val, value_type=vtype, text=str(val)))
        rows.append(OdsRow(cells=cells))
    doc = OdsDocument(
        sheets=[OdsSheet(name="Sheet1", rows=rows)],
        path="",
    )
    with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
        out = Path(f.name)
    write_ods(doc, out)
    return out


class TestGetColumnValues:
    def test_first_column(self):
        path = _make_ods([["Name", "Age"], ["Alice", 30], ["Bob", 25]])
        try:
            vals = get_column_values(path, 0)
            assert vals == ["Name", "Alice", "Bob"]
        finally:
            path.unlink(missing_ok=True)

    def test_second_column(self):
        path = _make_ods([["Name", "Age"], ["Alice", 30], ["Bob", 25]])
        try:
            vals = get_column_values(path, 1)
            assert len(vals) == 3
            assert vals[0] == "Age"
        finally:
            path.unlink(missing_ok=True)

    def test_out_of_range_column(self):
        path = _make_ods([["A", "B"], ["C", "D"]])
        try:
            vals = get_column_values(path, 5)
            assert all(v is None for v in vals)
        finally:
            path.unlink(missing_ok=True)

    def test_bad_sheet_index(self):
        path = _make_ods([["A"]])
        try:
            vals = get_column_values(path, 0, sheet_index=5)
            assert vals == []
        finally:
            path.unlink(missing_ok=True)

    def test_ragged_rows(self):
        path = _make_ods([["A", "B", "C"], ["X"]])
        try:
            vals = get_column_values(path, 2)
            assert vals[0] == "C"
            assert vals[1] is None
        finally:
            path.unlink(missing_ok=True)

    def test_empty_sheet(self):
        doc = OdsDocument(
            sheets=[OdsSheet(name="Empty", rows=[])],
            path="",
        )
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        write_ods(doc, out)
        try:
            vals = get_column_values(out, 0)
            assert vals == []
        finally:
            out.unlink(missing_ok=True)
