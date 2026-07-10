"""Tests for OdsModelDocument mutation API: set_cell_value() and save_to_file().

Sprint: ODS-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from ods.models import OdsModelDocument
from ods.ods_parser import OdsError, parse_ods_strict


SAMPLE_ODS = Path("samples/by-format/ods/valid/minimal-spreadsheet.ods")


class TestSetCellValue:
    def test_set_cell_value_string(self):
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        doc.set_cell_value(0, 0, 0, "NewValue")
        sheet = doc.get_sheet(0)
        assert sheet is not None
        cell = sheet.cell_at(0, 0)
        assert cell is not None
        assert cell.text == "NewValue"

    def test_set_cell_value_out_of_range_raises(self):
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        with pytest.raises(OdsError):
            doc.set_cell_value(99, 0, 0, "bad")

    def test_set_cell_extends_rows(self):
        """set_cell_value extends rows if needed (ODS writer behavior)."""
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        doc.set_cell_value(0, 100, 0, "Extended")
        sheet = doc.get_sheet(0)
        assert sheet is not None
        cell = sheet.cell_at(100, 0)
        assert cell is not None
        assert cell.text == "Extended"

    def test_set_cell_preserves_other_cells(self):
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        sheet0 = doc.get_sheet(0)
        if sheet0 is not None and sheet0.row_count > 0:
            original = sheet0.cell_at(0, 1)
            doc.set_cell_value(0, 0, 0, "Changed")
            after = doc.get_sheet(0).cell_at(0, 1)
            if original is not None and after is not None:
                assert after.text == original.text


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ods"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        with pytest.raises(OdsError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "dir" / "out.ods"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.ods"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_set_cell_roundtrip(self):
        """set_cell_value → save_to_file → from_file: new value visible."""
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        doc.set_cell_value(0, 0, 0, "RoundtripValue")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.ods"
            doc.save_to_file(dest)
            reloaded = OdsModelDocument.from_file(dest)
            sheet = reloaded.get_sheet(0)
            assert sheet is not None
            cell = sheet.cell_at(0, 0)
            assert cell is not None
            assert cell.text == "RoundtripValue"

    def test_set_cell_roundtrip_sheet_count_preserved(self):
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        original_count = doc.sheet_count
        doc.set_cell_value(0, 0, 0, "X")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.ods"
            doc.save_to_file(dest)
            reloaded = OdsModelDocument.from_file(dest)
            assert reloaded.sheet_count == original_count

    def test_multiple_set_cell_roundtrip(self):
        doc = OdsModelDocument.from_file(SAMPLE_ODS)
        doc.set_cell_value(0, 0, 0, "A")
        doc.set_cell_value(0, 0, 1, "B")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "multi.ods"
            doc.save_to_file(dest)
            reloaded = OdsModelDocument.from_file(dest)
            sheet = reloaded.get_sheet(0)
            assert sheet is not None
            assert sheet.cell_at(0, 0).text == "A"
            assert sheet.cell_at(0, 1).text == "B"
