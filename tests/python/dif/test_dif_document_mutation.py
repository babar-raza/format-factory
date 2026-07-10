"""Tests for DifDocument mutation API: set_cell_value() and save_to_file().

Sprint: DIF-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from dif.dif_parser import DifCell, DifDocument, DifError, parse_dif_strict


SAMPLE_DIF = Path("samples/by-format/dif/valid/minimal-2x2.dif")


def _make_doc() -> DifDocument:
    """Load the minimal-2x2.dif sample."""
    return parse_dif_strict(SAMPLE_DIF)


class TestSetCellValue:
    def test_set_existing_cell(self):
        doc = _make_doc()
        doc.set_cell_value(0, 0, "NewName")
        assert doc.rows[0][0].value == "NewName"

    def test_set_cell_mutates_in_place(self):
        doc = _make_doc()
        original_rows = doc.rows
        doc.set_cell_value(0, 0, "Changed")
        assert doc.rows is original_rows  # same list object

    def test_set_cell_out_of_range_row_raises(self):
        doc = _make_doc()
        with pytest.raises(DifError):
            doc.set_cell_value(99, 0, "bad")

    def test_set_cell_out_of_range_col_raises(self):
        doc = _make_doc()
        with pytest.raises(DifError):
            doc.set_cell_value(0, 99, "bad")

    def test_set_cell_numeric_type(self):
        doc = _make_doc()
        doc.set_cell_value(0, 1, 777, value_type="numeric")
        assert doc.rows[0][1].value == 777
        assert doc.rows[0][1].value_type == "numeric"

    def test_set_cell_preserves_other_cells(self):
        doc = _make_doc()
        original_val = doc.rows[0][1].value
        doc.set_cell_value(0, 0, "X")
        assert doc.rows[0][1].value == original_val


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.dif"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = _make_doc()
        with pytest.raises(DifError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.dif"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.dif"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_set_cell_roundtrip(self):
        """set_cell_value → save_to_file → parse_dif_strict: new value visible."""
        doc = _make_doc()
        doc.set_cell_value(0, 0, "Roundtrip")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.dif"
            doc.save_to_file(dest)
            reloaded = parse_dif_strict(dest)
            assert reloaded.rows[0][0].value == "Roundtrip"

    def test_roundtrip_other_cell_preserved(self):
        doc = _make_doc()
        orig_val = doc.rows[0][1].value
        doc.set_cell_value(0, 0, "Modified")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.dif"
            doc.save_to_file(dest)
            reloaded = parse_dif_strict(dest)
            assert reloaded.rows[0][1].value == orig_val

    def test_multiple_mutations_roundtrip(self):
        doc = _make_doc()
        doc.set_cell_value(0, 0, "A")
        doc.set_cell_value(0, 1, "B")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "multi.dif"
            doc.save_to_file(dest)
            reloaded = parse_dif_strict(dest)
            assert reloaded.rows[0][0].value == "A"
            assert reloaded.rows[0][1].value == "B"
