"""Tests for SylkModelDocument mutation API: set_cell_value() and save_to_file().

Sprint: SYLK-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from sylk.models import SylkModelDocument
from sylk.sylk_parser import SylkError


SAMPLE_SYLK = Path("samples/by-format/sylk/valid/minimal-2x2.slk")


class TestSetCellValue:
    def test_set_cell_value_existing(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        doc.set_cell_value(1, 1, "Mutated")
        cell = next(c for c in doc._parsed.cells if c.row == 1 and c.col == 1)
        assert cell.value == "Mutated"

    def test_set_cell_value_new_cell(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        before = doc.cell_count
        doc.set_cell_value(3, 1, "NewRow")
        assert doc.cell_count == before + 1

    def test_set_cell_bad_row_raises(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        with pytest.raises(SylkError):
            doc.set_cell_value(0, 1, "x")

    def test_set_cell_bad_col_raises(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        with pytest.raises(SylkError):
            doc.set_cell_value(1, 0, "x")

    def test_set_cell_value_type(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        doc.set_cell_value(2, 2, 99, "numeric")
        cell = next(c for c in doc._parsed.cells if c.row == 2 and c.col == 2)
        assert cell.value_type == "numeric"

    def test_set_cell_preserves_other_cells(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        original_count = doc.cell_count
        doc.set_cell_value(1, 1, "Changed")
        assert doc.cell_count == original_count


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.slk"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        with pytest.raises(SylkError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.slk"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.slk"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_set_cell_value_roundtrip(self):
        """set_cell_value → save_to_file → from_file: mutated value visible."""
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        doc.set_cell_value(1, 1, "RoundtripVal")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.slk"
            doc.save_to_file(dest)
            reloaded = SylkModelDocument.from_file(dest)
            cell = next((c for c in reloaded._parsed.cells if c.row == 1 and c.col == 1), None)
            assert cell is not None
            assert cell.value == "RoundtripVal"

    def test_roundtrip_row_col_count_preserved(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        original_rows = doc._parsed.rows
        doc.set_cell_value(1, 1, "X")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.slk"
            doc.save_to_file(dest)
            reloaded = SylkModelDocument.from_file(dest)
            assert reloaded._parsed.rows >= original_rows

    def test_multiple_mutations_roundtrip(self):
        doc = SylkModelDocument.from_file(SAMPLE_SYLK)
        doc.set_cell_value(1, 1, "AAA")
        doc.set_cell_value(2, 2, "BBB")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.slk"
            doc.save_to_file(dest)
            reloaded = SylkModelDocument.from_file(dest)
            cell11 = next((c for c in reloaded._parsed.cells if c.row == 1 and c.col == 1), None)
            cell22 = next((c for c in reloaded._parsed.cells if c.row == 2 and c.col == 2), None)
            assert cell11 is not None and cell11.value == "AAA"
            assert cell22 is not None and cell22.value == "BBB"
