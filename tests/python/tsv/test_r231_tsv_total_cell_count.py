"""Tests for tsv_total_cell_count and tsv_average_cell_length.

Product deepening: TSV analytics — TC-H3-002-TSV / PDC-TSV-TOTAL-CELL-COUNT-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import (
    tsv_total_cell_count,
    tsv_average_cell_length,
    write_tsv,
)

SAMPLES = _REPO / "samples" / "by-format" / "tsv"


def _make_tsv(tmp_path, name, rows):
    path = tmp_path / f"{name}.tsv"
    write_tsv(rows, str(path))
    return path


class TestTsvTotalCellCount:
    def test_2x2(self, tmp_path):
        """write_tsv treats row[0] as header; parse_tsv_strict returns data rows only."""
        f = _make_tsv(tmp_path, "2x2", [["h1", "h2"], ["a", "b"], ["c", "d"]])
        assert tsv_total_cell_count(f) == 4

    def test_3x1(self, tmp_path):
        f = _make_tsv(tmp_path, "3x1", [["h"], ["a"], ["b"], ["c"]])
        assert tsv_total_cell_count(f) == 3

    def test_empty(self, tmp_path):
        path = tmp_path / "empty.tsv"
        path.write_text("")
        assert tsv_total_cell_count(path) == 0

    def test_single_cell(self, tmp_path):
        f = _make_tsv(tmp_path, "single", [["hello"]])
        assert tsv_total_cell_count(f) == 1

    def test_returns_int(self, tmp_path):
        f = _make_tsv(tmp_path, "type", [["a", "b"]])
        assert isinstance(tsv_total_cell_count(f), int)

    def test_from_sample(self):
        path = SAMPLES / "minimal-2x2.tsv"
        if path.exists():
            result = tsv_total_cell_count(path)
            assert isinstance(result, int)
            assert result >= 4


class TestTsvAverageCellLength:
    def test_uniform(self, tmp_path):
        f = _make_tsv(tmp_path, "uniform", [["ab", "cd"], ["ef", "gh"]])
        assert tsv_average_cell_length(f) == 2.0

    def test_mixed(self, tmp_path):
        f = _make_tsv(tmp_path, "mixed", [["a", "abc"]])
        result = tsv_average_cell_length(f)
        assert result == 2.0

    def test_with_empty_cells(self, tmp_path):
        f = _make_tsv(tmp_path, "empties", [["hello", ""], ["", "world"]])
        result = tsv_average_cell_length(f)
        assert result == 5.0

    def test_all_empty(self, tmp_path):
        f = _make_tsv(tmp_path, "allempty", [["", ""], ["", ""]])
        assert tsv_average_cell_length(f) == 0.0

    def test_returns_float(self, tmp_path):
        f = _make_tsv(tmp_path, "type2", [["abc"]])
        assert isinstance(tsv_average_cell_length(f), float)

    def test_from_sample(self):
        path = SAMPLES / "minimal-2x2.tsv"
        if path.exists():
            result = tsv_average_cell_length(path)
            assert isinstance(result, float)
            assert result >= 0.0
