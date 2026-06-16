"""Tests for tsv_min_cell_length and tsv_all_rows_same_length (Sprint 29)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv import tsv_min_cell_length, tsv_all_rows_same_length


def _write(tmp_path, name, content):
    p = tmp_path / f"{name}.tsv"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestTsvMinCellLength:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt", "h\nab\ncd\n")
        assert isinstance(tsv_min_cell_length(p), int)

    def test_exact_min(self, tmp_path):
        # data rows: ['1', '22'] and ['333', '4'] → min = 1
        p = _write(tmp_path, "em", "h1\th2\n1\t22\n333\t4\n")
        assert tsv_min_cell_length(p) == 1

    def test_single_char_cells(self, tmp_path):
        # all single-char → min = 1
        p = _write(tmp_path, "sc", "col\na\nb\nc\n")
        assert tsv_min_cell_length(p) == 1

    def test_nonnegative(self, tmp_path):
        p = _write(tmp_path, "nn", "x\nhello\n")
        assert tsv_min_cell_length(p) >= 0

    def test_longer_cells(self, tmp_path):
        # data: ['abc', 'de'] → min = 2
        p = _write(tmp_path, "lc", "h1\th2\nabc\tde\n")
        assert tsv_min_cell_length(p) == 2


class TestTsvAllRowsSameLength:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt2", "h\na\nb\n")
        assert isinstance(tsv_all_rows_same_length(p), bool)

    def test_uniform_rows(self, tmp_path):
        # header + 2 data rows, each 2 fields → True
        p = _write(tmp_path, "ur", "h1\th2\n1\t2\n3\t4\n")
        assert tsv_all_rows_same_length(p) is True

    def test_empty_file_is_true(self, tmp_path):
        p = _write(tmp_path, "ef", "")
        assert tsv_all_rows_same_length(p) is True

    def test_single_row(self, tmp_path):
        p = _write(tmp_path, "sr", "h\nval\n")
        assert tsv_all_rows_same_length(p) is True

    def test_three_col_uniform(self, tmp_path):
        # 3 data rows all 3 cols → True
        p = _write(tmp_path, "tc", "h1\th2\th3\na\tb\tc\n1\t2\t3\n")
        assert tsv_all_rows_same_length(p) is True
