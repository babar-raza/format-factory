"""Tests for GnumericDocument mutation API: set_cell_value() and save_to_file().

Sprint: GNUMERIC-PYTHON-MUTATION-001
"""
import tempfile
from pathlib import Path

import pytest

from gnumeric.gnumeric_codec import create_gnumeric
from gnumeric.models import GnumericDocument


def _make_doc() -> GnumericDocument:
    """Create a small single-sheet GnumericDocument with 2 cells."""
    model = create_gnumeric([
        {"name": "Sheet1", "rows": [["hello", "world"]]}
    ])
    return GnumericDocument(model)


class TestSetCellValue:
    def test_set_existing_cell(self):
        doc = _make_doc()
        doc.set_cell_value(0, 0, 0, "changed")
        assert doc.get_cell_value(0, 0, 0) == "changed"

    def test_set_new_cell(self):
        doc = _make_doc()
        doc.set_cell_value(0, 1, 0, "newval")
        assert doc.get_cell_value(0, 1, 0) == "newval"

    def test_set_cell_increases_cell_count_for_new_cell(self):
        doc = _make_doc()
        before = doc.cell_count
        doc.set_cell_value(0, 5, 5, "extra")
        assert doc.cell_count == before + 1

    def test_set_cell_preserves_other_cells(self):
        doc = _make_doc()
        doc.set_cell_value(0, 0, 0, "X")
        assert doc.get_cell_value(0, 0, 1) == "world"

    def test_set_cell_out_of_range_raises(self):
        from gnumeric.gnumeric_codec import GnumericError
        doc = _make_doc()
        with pytest.raises(GnumericError):
            doc.set_cell_value(99, 0, 0, "bad")

    def test_set_cell_non_str_raises(self):
        doc = _make_doc()
        with pytest.raises(TypeError):
            doc.set_cell_value(0, 0, 0, 42)  # type: ignore[arg-type]


class TestSaveToFile:
    def test_save_creates_file(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.gnumeric"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_empty_path_raises(self):
        from gnumeric.gnumeric_codec import GnumericError
        doc = _make_doc()
        with pytest.raises(GnumericError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "sub" / "dir" / "out.gnumeric"
            doc.save_to_file(dest)
            assert dest.exists()

    def test_save_file_is_nonzero(self):
        doc = _make_doc()
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "out.gnumeric"
            doc.save_to_file(dest)
            assert dest.stat().st_size > 0


class TestMutationRoundtrip:
    def test_set_cell_roundtrip(self):
        """set_cell_value → save_to_file → from_file: new value visible."""
        doc = _make_doc()
        doc.set_cell_value(0, 0, 0, "roundtrip_value")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt.gnumeric"
            doc.save_to_file(dest)
            reloaded = GnumericDocument.from_file(dest)
            assert reloaded.get_cell_value(0, 0, 0) == "roundtrip_value"

    def test_set_cell_roundtrip_other_cell_preserved(self):
        """After set_cell_value + roundtrip, other cells remain intact."""
        doc = _make_doc()
        doc.set_cell_value(0, 0, 0, "modified")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "rt2.gnumeric"
            doc.save_to_file(dest)
            reloaded = GnumericDocument.from_file(dest)
            assert reloaded.get_cell_value(0, 0, 1) == "world"

    def test_multiple_set_cell_roundtrip(self):
        """Multiple mutations survive save/reload."""
        doc = _make_doc()
        doc.set_cell_value(0, 0, 0, "A")
        doc.set_cell_value(0, 0, 1, "B")
        doc.set_cell_value(0, 1, 0, "C")
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "multi.gnumeric"
            doc.save_to_file(dest)
            reloaded = GnumericDocument.from_file(dest)
            assert reloaded.get_cell_value(0, 0, 0) == "A"
            assert reloaded.get_cell_value(0, 0, 1) == "B"
            assert reloaded.get_cell_value(0, 1, 0) == "C"
