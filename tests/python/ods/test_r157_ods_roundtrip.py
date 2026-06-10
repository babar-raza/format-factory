"""
test_r157_ods_roundtrip.py — ODS write + roundtrip proof tests.

Tests:
  1. write_ods produces a valid ODS file
  2. roundtrip preserves sheet names
  3. roundtrip preserves row/column counts
  4. roundtrip preserves string cell values
  5. roundtrip preserves numeric cell values
  6. roundtrip handles empty document
  7. roundtrip handles multiple sheets
  8. document_to_ods_bytes produces valid ZIP
"""
from __future__ import annotations

import sys
import zipfile
from io import BytesIO
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.python.ods.ods_parser import (
    OdsCell,
    OdsDocument,
    OdsRow,
    OdsSheet,
    parse_ods_strict,
)
from src.python.ods.ods_writer import document_to_ods_bytes, write_ods


def _make_doc(
    sheet_name: str = "Sheet1",
    rows: list[list[OdsCell]] | None = None,
) -> OdsDocument:
    if rows is None:
        rows = [
            [OdsCell(value="10", value_type="float", text="10"),
             OdsCell(value=None, value_type="string", text="Alpha")],
            [OdsCell(value="20", value_type="float", text="20"),
             OdsCell(value=None, value_type="string", text="Beta")],
        ]
    ods_rows = [OdsRow(cells=r) for r in rows]
    sheet = OdsSheet(name=sheet_name, rows=ods_rows)
    return OdsDocument(sheets=[sheet])


class TestOdsRoundtrip:
    def test_write_produces_file(self, tmp_path):
        doc = _make_doc()
        out = tmp_path / "test.ods"
        write_ods(doc, out)
        assert out.exists()
        assert out.stat().st_size > 0

    def test_roundtrip_preserves_sheet_name(self, tmp_path):
        doc = _make_doc(sheet_name="MyData")
        out = tmp_path / "test.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert len(reloaded.sheets) == 1
        assert reloaded.sheets[0].name == "MyData"

    def test_roundtrip_preserves_row_count(self, tmp_path):
        doc = _make_doc()
        out = tmp_path / "test.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert len(reloaded.sheets[0].rows) == 2

    def test_roundtrip_preserves_column_count(self, tmp_path):
        doc = _make_doc()
        out = tmp_path / "test.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert len(reloaded.sheets[0].rows[0].cells) == 2

    def test_roundtrip_preserves_string_values(self, tmp_path):
        rows = [
            [OdsCell(value=None, value_type="string", text="Hello")],
            [OdsCell(value=None, value_type="string", text="World")],
        ]
        doc = _make_doc(rows=rows)
        out = tmp_path / "test.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert reloaded.sheets[0].rows[0].cells[0].text == "Hello"
        assert reloaded.sheets[0].rows[1].cells[0].text == "World"

    def test_roundtrip_preserves_numeric_values(self, tmp_path):
        rows = [
            [OdsCell(value="42", value_type="float", text="42")],
            [OdsCell(value="3.14", value_type="float", text="3.14")],
        ]
        doc = _make_doc(rows=rows)
        out = tmp_path / "test.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert reloaded.sheets[0].rows[0].cells[0].value_type == "float"

    def test_roundtrip_empty_document(self, tmp_path):
        doc = OdsDocument(sheets=[OdsSheet(name="Empty", rows=[])])
        out = tmp_path / "empty.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert len(reloaded.sheets) == 1
        assert reloaded.sheets[0].name == "Empty"

    def test_roundtrip_multiple_sheets(self, tmp_path):
        s1 = OdsSheet(name="First", rows=[OdsRow(cells=[OdsCell(text="A")])])
        s2 = OdsSheet(name="Second", rows=[OdsRow(cells=[OdsCell(text="B")])])
        doc = OdsDocument(sheets=[s1, s2])
        out = tmp_path / "multi.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert len(reloaded.sheets) == 2
        names = [s.name for s in reloaded.sheets]
        assert "First" in names
        assert "Second" in names

    def test_document_to_bytes_is_valid_zip(self):
        doc = _make_doc()
        data = document_to_ods_bytes(doc)
        assert isinstance(data, bytes)
        zf = zipfile.ZipFile(BytesIO(data))
        names = zf.namelist()
        assert "mimetype" in names
        assert "content.xml" in names
        assert "META-INF/manifest.xml" in names

    def test_document_to_bytes_mimetype_first(self):
        doc = _make_doc()
        data = document_to_ods_bytes(doc)
        zf = zipfile.ZipFile(BytesIO(data))
        assert zf.namelist()[0] == "mimetype"
