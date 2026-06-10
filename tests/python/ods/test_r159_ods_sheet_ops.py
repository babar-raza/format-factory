"""Tests for ODS add_sheet, remove_sheet, rename_sheet.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT19-001
Covers: sheet management operations with roundtrip verification
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell, parse_ods_strict
from ods.ods_writer import write_ods, add_sheet, remove_sheet, rename_sheet


def _make_doc():
    return OdsDocument(
        sheets=[
            OdsSheet(name="Alpha", rows=[
                OdsRow(cells=[OdsCell(value="A1", value_type="string", text="A1")]),
            ]),
            OdsSheet(name="Beta", rows=[
                OdsRow(cells=[OdsCell(value="B1", value_type="string", text="B1")]),
            ]),
        ],
        path="",
    )


class TestAddSheet:
    def test_add_appends_by_default(self):
        doc = _make_doc()
        ok, _ = add_sheet(doc, "Gamma")
        assert ok
        assert len(doc.sheets) == 3
        assert doc.sheets[2].name == "Gamma"

    def test_add_at_position(self):
        doc = _make_doc()
        ok, _ = add_sheet(doc, "First", position=0)
        assert ok
        assert doc.sheets[0].name == "First"
        assert doc.sheets[1].name == "Alpha"

    def test_add_duplicate_fails(self):
        doc = _make_doc()
        ok, msg = add_sheet(doc, "Alpha")
        assert not ok

    def test_add_roundtrip(self):
        doc = _make_doc()
        add_sheet(doc, "New")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert len(doc2.sheets) == 3
            assert doc2.sheets[2].name == "New"
        finally:
            out.unlink(missing_ok=True)


class TestRemoveSheet:
    def test_remove_existing(self):
        doc = _make_doc()
        ok, _ = remove_sheet(doc, "Beta")
        assert ok
        assert len(doc.sheets) == 1
        assert doc.sheets[0].name == "Alpha"

    def test_remove_nonexistent_fails(self):
        doc = _make_doc()
        ok, msg = remove_sheet(doc, "NotHere")
        assert not ok

    def test_remove_roundtrip(self):
        doc = _make_doc()
        remove_sheet(doc, "Alpha")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert len(doc2.sheets) == 1
            assert doc2.sheets[0].name == "Beta"
        finally:
            out.unlink(missing_ok=True)


class TestRenameSheet:
    def test_rename_existing(self):
        doc = _make_doc()
        ok, _ = rename_sheet(doc, "Alpha", "Renamed")
        assert ok
        assert doc.sheets[0].name == "Renamed"

    def test_rename_nonexistent_fails(self):
        doc = _make_doc()
        ok, _ = rename_sheet(doc, "NotHere", "X")
        assert not ok

    def test_rename_to_existing_fails(self):
        doc = _make_doc()
        ok, _ = rename_sheet(doc, "Alpha", "Beta")
        assert not ok

    def test_rename_roundtrip(self):
        doc = _make_doc()
        rename_sheet(doc, "Alpha", "Primary")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].name == "Primary"
            assert doc2.sheets[1].name == "Beta"
        finally:
            out.unlink(missing_ok=True)
