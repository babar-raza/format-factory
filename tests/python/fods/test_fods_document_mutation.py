"""Tests for FodsDocument mutation API: set_cell_value() and save_to_file().

Sprint: FODS-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from fods.models import FodsDocument
from fods.exceptions import FodsError


SAMPLE_FODS = Path("samples/by-format/fods/valid/simple.fods")


class TestSetCellValue:
    def test_set_cell_value_string(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        doc.set_cell_value(0, 0, 0, "Mutated")
        cells = doc._spec_doc._data["sheets"][0]["rows"][0]["cells"]
        assert cells[0]["value"] == "Mutated"

    def test_set_cell_out_of_sheet_range_raises(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        with pytest.raises(FodsError):
            doc.set_cell_value(99, 0, 0, "x")

    def test_set_cell_out_of_row_range_raises(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        with pytest.raises(FodsError):
            doc.set_cell_value(0, 99, 0, "x")

    def test_set_cell_out_of_col_range_raises(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        with pytest.raises(FodsError):
            doc.set_cell_value(0, 0, 99, "x")

    def test_set_cell_value_type(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        doc.set_cell_value(0, 1, 1, "100", "float")
        cells = doc._spec_doc._data["sheets"][0]["rows"][1]["cells"]
        assert cells[1]["value_type"] == "float"

    def test_set_cell_preserves_other_cells(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        before = doc._spec_doc._data["sheets"][0]["rows"][0]["cells"][1]["value"]
        doc.set_cell_value(0, 0, 0, "Changed")
        after = doc._spec_doc._data["sheets"][0]["rows"][0]["cells"][1]["value"]
        assert after == before


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.fods"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        with pytest.raises(FodsError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.fods"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.fods"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_set_cell_roundtrip(self):
        """set_cell_value → save_to_file → from_file: mutated value visible."""
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        doc.set_cell_value(0, 0, 0, "RoundtripValue")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.fods"
            doc.save_to_file(dest)
            reloaded = FodsDocument.from_file(str(dest))
            cells = reloaded._spec_doc._data["sheets"][0]["rows"][0]["cells"]
            assert cells[0]["value"] == "RoundtripValue"

    def test_roundtrip_sheet_count_preserved(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        original_sheets = doc.sheet_count
        doc.set_cell_value(0, 0, 0, "X")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.fods"
            doc.save_to_file(dest)
            reloaded = FodsDocument.from_file(str(dest))
            assert reloaded.sheet_count == original_sheets

    def test_multiple_mutations_roundtrip(self):
        doc = FodsDocument.from_file(str(SAMPLE_FODS))
        doc.set_cell_value(0, 0, 0, "A-mutated")
        doc.set_cell_value(0, 1, 0, "B-mutated")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.fods"
            doc.save_to_file(dest)
            reloaded = FodsDocument.from_file(str(dest))
            rows = reloaded._spec_doc._data["sheets"][0]["rows"]
            assert rows[0]["cells"][0]["value"] == "A-mutated"
            assert rows[1]["cells"][0]["value"] == "B-mutated"
