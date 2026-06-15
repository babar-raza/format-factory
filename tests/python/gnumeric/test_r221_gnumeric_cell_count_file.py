"""Tests for gnumeric_cell_count_file — R221 product deepening."""

import gzip
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_cell_count_file, create_gnumeric, write_gnumeric


def _make_gnumeric(tmp_path, name, sheets):
    """Helper: create a .gnumeric file from sheet specs."""
    model = create_gnumeric(sheets)
    path = tmp_path / name
    write_gnumeric(model, path)
    return path


class TestGnumericCellCountFile:
    def test_single_sheet(self, tmp_path):
        path = _make_gnumeric(tmp_path, "one.gnumeric", [
            {"name": "Sheet1", "rows": [["a", "b", "c"], ["d", "e", "f"]]}
        ])
        assert gnumeric_cell_count_file(path) == 6

    def test_empty_sheet(self, tmp_path):
        path = _make_gnumeric(tmp_path, "empty.gnumeric", [
            {"name": "Sheet1", "rows": []}
        ])
        assert gnumeric_cell_count_file(path) == 0

    def test_second_sheet(self, tmp_path):
        path = _make_gnumeric(tmp_path, "two.gnumeric", [
            {"name": "Sheet1", "rows": [["x"]]},
            {"name": "Sheet2", "rows": [["a", "b"], ["c", "d"], ["e", "f"]]}
        ])
        assert gnumeric_cell_count_file(path, sheet_idx=1) == 6

    def test_default_sheet_idx(self, tmp_path):
        path = _make_gnumeric(tmp_path, "default.gnumeric", [
            {"name": "Sheet1", "rows": [["1", "2"]]}
        ])
        assert gnumeric_cell_count_file(path) == 2

    def test_str_path(self, tmp_path):
        path = _make_gnumeric(tmp_path, "str.gnumeric", [
            {"name": "Sheet1", "rows": [["val"]]}
        ])
        assert gnumeric_cell_count_file(str(path)) == 1

    def test_mixed_empty_nonempty(self, tmp_path):
        path = _make_gnumeric(tmp_path, "mixed.gnumeric", [
            {"name": "Sheet1", "rows": [["a", "", "c"], ["", "b", ""]]}
        ])
        # count_nonempty_cells only counts non-empty cells
        result = gnumeric_cell_count_file(path)
        assert result == 3

    def test_invalid_sheet_idx_raises(self, tmp_path):
        from gnumeric.gnumeric_codec import GnumericError
        path = _make_gnumeric(tmp_path, "idx.gnumeric", [
            {"name": "Sheet1", "rows": [["x"]]}
        ])
        with pytest.raises(GnumericError):
            gnumeric_cell_count_file(path, sheet_idx=99)
