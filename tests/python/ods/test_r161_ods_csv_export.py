"""Tests for ODS ods_to_csv export.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT22-001
Covers: CSV export from ODS files
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell, ods_to_csv
from ods.ods_writer import write_ods


def _make_ods(rows_data, sheet_name="Sheet1"):
    rows = []
    for row_vals in rows_data:
        cells = []
        for val in row_vals:
            vtype = "float" if isinstance(val, (int, float)) else "string"
            cells.append(OdsCell(value=val, value_type=vtype, text=str(val)))
        rows.append(OdsRow(cells=cells))
    doc = OdsDocument(
        sheets=[OdsSheet(name=sheet_name, rows=rows)],
        path="",
    )
    with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
        out = Path(f.name)
    write_ods(doc, out)
    return out


class TestOdsToCsv:
    def test_basic_export(self):
        path = _make_ods([["Name", "Age"], ["Alice", 30]])
        try:
            csv_str = ods_to_csv(path)
            lines = csv_str.strip().split("\r\n")
            assert len(lines) == 2
            assert lines[0] == "Name,Age"
            assert lines[1] == "Alice,30"
        finally:
            path.unlink(missing_ok=True)

    def test_empty_sheet(self):
        doc = OdsDocument(sheets=[OdsSheet(name="Empty", rows=[])], path="")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        write_ods(doc, out)
        try:
            csv_str = ods_to_csv(out)
            assert csv_str == ""
        finally:
            out.unlink(missing_ok=True)

    def test_bad_sheet_index(self):
        path = _make_ods([["A"]])
        try:
            csv_str = ods_to_csv(path, sheet_index=5)
            assert csv_str == ""
        finally:
            path.unlink(missing_ok=True)

    def test_numeric_formatting(self):
        path = _make_ods([[1.0, 2.5, 3.0]])
        try:
            csv_str = ods_to_csv(path)
            assert "1," in csv_str
            assert "2.5" in csv_str
            assert "3\r\n" in csv_str or csv_str.rstrip().endswith("3")
        finally:
            path.unlink(missing_ok=True)

    def test_special_characters(self):
        path = _make_ods([["hello, world", "line1"]])
        try:
            csv_str = ods_to_csv(path)
            assert '"hello, world"' in csv_str
        finally:
            path.unlink(missing_ok=True)

    def test_multiple_rows(self):
        path = _make_ods([["A", "B"], ["C", "D"], ["E", "F"]])
        try:
            csv_str = ods_to_csv(path)
            lines = csv_str.strip().split("\r\n")
            assert len(lines) == 3
        finally:
            path.unlink(missing_ok=True)
