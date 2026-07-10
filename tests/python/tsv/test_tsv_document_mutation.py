"""Tests for TsvDocument mutation API: add_row(), set_cell(), save_to_file().

Sprint: TSV-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from tsv.models import TsvDocument
from tsv.exceptions import TsvError


SAMPLE_TSV = Path("samples/by-format/tsv/minimal-2x2.tsv")


class TestAddRow:
    def test_add_row_appends(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        before = doc.row_count
        doc.add_row(["Charlie", "40"])
        assert doc.row_count == before + 1

    def test_add_row_values_correct(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        doc.add_row(["Charlie", "40"])
        assert doc._data["rows"][-1] == ["Charlie", "40"]

    def test_add_row_none_raises(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        with pytest.raises(TsvError):
            doc.add_row(None)  # type: ignore[arg-type]

    def test_add_row_empty_row(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        before = doc.row_count
        doc.add_row([])
        assert doc.row_count == before + 1

    def test_add_multiple_rows(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        before = doc.row_count
        doc.add_row(["D", "1"])
        doc.add_row(["E", "2"])
        assert doc.row_count == before + 2

    def test_existing_rows_intact(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        existing = list(doc._data["rows"])
        doc.add_row(["X", "99"])
        after = doc._data["rows"][:-1]
        assert after == existing


class TestSetCell:
    def test_set_cell_string(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        doc.set_cell(0, 0, "Zara")
        assert doc._data["rows"][0][0] == "Zara"

    def test_set_cell_out_of_row_range_raises(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        with pytest.raises(TsvError):
            doc.set_cell(99, 0, "x")

    def test_set_cell_out_of_col_range_raises(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        with pytest.raises(TsvError):
            doc.set_cell(0, 99, "x")

    def test_set_cell_preserves_other_cells(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        original_row1 = list(doc._data["rows"][1])
        doc.set_cell(0, 0, "Mutated")
        assert doc._data["rows"][1] == original_row1


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.tsv"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        with pytest.raises(TsvError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "out.tsv"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.tsv"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_add_row_roundtrip(self):
        """add_row → save_to_file → from_file: new row visible."""
        doc = TsvDocument.from_file(SAMPLE_TSV)
        doc.add_row(["RoundtripName", "99"])
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.tsv"
            doc.save_to_file(dest)
            reloaded = TsvDocument.from_file(dest)
            all_rows = reloaded._data.get("rows", [])
            assert any("RoundtripName" in row for row in all_rows)

    def test_set_cell_roundtrip(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        doc.set_cell(0, 0, "MutatedName")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.tsv"
            doc.save_to_file(dest)
            reloaded = TsvDocument.from_file(dest)
            rows = reloaded._data.get("rows", [])
            assert any("MutatedName" in row for row in rows)

    def test_roundtrip_row_count_preserved(self):
        doc = TsvDocument.from_file(SAMPLE_TSV)
        original_count = doc.row_count
        doc.add_row(["Extra", "0"])
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt3.tsv"
            doc.save_to_file(dest)
            reloaded = TsvDocument.from_file(dest)
            assert reloaded.row_count == original_count + 1
