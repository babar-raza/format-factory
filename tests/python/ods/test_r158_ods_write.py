"""Tests for ODS write capability (GAP-ODS-WRITE-001).

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT17-001
Covers: write_ods, document_to_ods_bytes, roundtrip parse→write→parse
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell, parse_ods_strict
from ods.ods_writer import write_ods, document_to_ods_bytes


def _make_doc(sheets=None):
    """Build a minimal OdsDocument for testing."""
    if sheets is None:
        sheets = [
            OdsSheet(
                name="Sheet1",
                rows=[
                    OdsRow(cells=[
                        OdsCell(value="Name", value_type="string", text="Name"),
                        OdsCell(value="Age", value_type="string", text="Age"),
                    ]),
                    OdsRow(cells=[
                        OdsCell(value="Alice", value_type="string", text="Alice"),
                        OdsCell(value=30.0, value_type="float", text="30"),
                    ]),
                    OdsRow(cells=[
                        OdsCell(value="Bob", value_type="string", text="Bob"),
                        OdsCell(value=25.0, value_type="float", text="25"),
                    ]),
                ],
            )
        ]
    return OdsDocument(sheets=sheets, path="")


class TestOdsWriteBasic:
    """Basic write and serialization tests."""

    def test_write_ods_creates_file(self):
        doc = _make_doc()
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            assert out.exists()
            assert out.stat().st_size > 0
        finally:
            out.unlink(missing_ok=True)

    def test_document_to_ods_bytes_returns_bytes(self):
        doc = _make_doc()
        data = document_to_ods_bytes(doc)
        assert isinstance(data, bytes)
        assert len(data) > 0

    def test_written_file_is_valid_zip(self):
        import zipfile
        doc = _make_doc()
        data = document_to_ods_bytes(doc)
        import io
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            names = zf.namelist()
            assert "mimetype" in names
            assert "content.xml" in names
            assert "META-INF/manifest.xml" in names

    def test_mimetype_is_correct(self):
        import zipfile, io
        doc = _make_doc()
        data = document_to_ods_bytes(doc)
        with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
            mime = zf.read("mimetype").decode("utf-8").strip()
            assert mime == "application/vnd.oasis.opendocument.spreadsheet"


class TestOdsRoundtrip:
    """Roundtrip tests: build doc → write → parse → verify."""

    def test_roundtrip_preserves_sheet_count(self):
        doc = _make_doc()
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert len(doc2.sheets) == len(doc.sheets)
        finally:
            out.unlink(missing_ok=True)

    def test_roundtrip_preserves_sheet_name(self):
        doc = _make_doc()
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].name == "Sheet1"
        finally:
            out.unlink(missing_ok=True)

    def test_roundtrip_preserves_row_count(self):
        doc = _make_doc()
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert len(doc2.sheets[0].rows) == 3
        finally:
            out.unlink(missing_ok=True)

    def test_roundtrip_preserves_string_values(self):
        doc = _make_doc()
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].rows[0].cells[0].value == "Name"
            assert doc2.sheets[0].rows[1].cells[0].value == "Alice"
            assert doc2.sheets[0].rows[2].cells[0].value == "Bob"
        finally:
            out.unlink(missing_ok=True)

    def test_roundtrip_preserves_float_values(self):
        doc = _make_doc()
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].rows[1].cells[1].value == 30.0
            assert doc2.sheets[0].rows[2].cells[1].value == 25.0
        finally:
            out.unlink(missing_ok=True)

    def test_roundtrip_preserves_value_types(self):
        doc = _make_doc()
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].rows[0].cells[0].value_type == "string"
            assert doc2.sheets[0].rows[1].cells[1].value_type == "float"
        finally:
            out.unlink(missing_ok=True)


class TestOdsWriteMultiSheet:
    """Multi-sheet write tests."""

    def test_write_two_sheets(self):
        sheets = [
            OdsSheet(name="Data", rows=[
                OdsRow(cells=[OdsCell(value="x", value_type="string", text="x")]),
            ]),
            OdsSheet(name="Summary", rows=[
                OdsRow(cells=[OdsCell(value="total", value_type="string", text="total")]),
            ]),
        ]
        doc = OdsDocument(sheets=sheets, path="")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert len(doc2.sheets) == 2
            assert doc2.sheets[0].name == "Data"
            assert doc2.sheets[1].name == "Summary"
        finally:
            out.unlink(missing_ok=True)

    def test_write_empty_sheet(self):
        sheets = [OdsSheet(name="Empty", rows=[])]
        doc = OdsDocument(sheets=sheets, path="")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert len(doc2.sheets) == 1
            assert doc2.sheets[0].name == "Empty"
            assert len(doc2.sheets[0].rows) == 0
        finally:
            out.unlink(missing_ok=True)


class TestOdsWriteEdgeCases:
    """Edge case tests."""

    def test_write_empty_cell(self):
        sheets = [OdsSheet(name="S", rows=[
            OdsRow(cells=[OdsCell(value=None, value_type="", text="")]),
        ])]
        doc = OdsDocument(sheets=sheets, path="")
        data = document_to_ods_bytes(doc)
        assert len(data) > 0

    def test_write_date_value(self):
        sheets = [OdsSheet(name="S", rows=[
            OdsRow(cells=[OdsCell(value="2026-01-15", value_type="date", text="2026-01-15")]),
        ])]
        doc = OdsDocument(sheets=sheets, path="")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].rows[0].cells[0].value == "2026-01-15"
        finally:
            out.unlink(missing_ok=True)

    def test_write_boolean_value(self):
        sheets = [OdsSheet(name="S", rows=[
            OdsRow(cells=[OdsCell(value="true", value_type="boolean", text="true")]),
        ])]
        doc = OdsDocument(sheets=sheets, path="")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].rows[0].cells[0].value_type == "boolean"
        finally:
            out.unlink(missing_ok=True)

    def test_double_roundtrip_stability(self):
        """Write → parse → write → parse produces same data."""
        doc = _make_doc()
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out1 = Path(f.name)
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out2 = Path(f.name)
        try:
            write_ods(doc, out1)
            doc2 = parse_ods_strict(out1)
            write_ods(doc2, out2)
            doc3 = parse_ods_strict(out2)
            assert len(doc3.sheets) == len(doc.sheets)
            assert len(doc3.sheets[0].rows) == len(doc.sheets[0].rows)
            for r_idx, (r_orig, r_rt) in enumerate(zip(doc.sheets[0].rows, doc3.sheets[0].rows)):
                for c_idx, (c_orig, c_rt) in enumerate(zip(r_orig.cells, r_rt.cells)):
                    assert c_rt.value == c_orig.value, f"Mismatch at ({r_idx},{c_idx})"
        finally:
            out1.unlink(missing_ok=True)
            out2.unlink(missing_ok=True)
