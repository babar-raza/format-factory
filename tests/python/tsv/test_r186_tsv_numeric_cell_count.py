"""
tests/python/tsv/test_r186_tsv_numeric_cell_count.py

Tests for tsv_numeric_cell_count() — count cells whose string value parses as float.
Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT54-001
"""
from __future__ import annotations

import pytest
from pathlib import Path

from src.python.tsv.tsv_parser import tsv_numeric_cell_count, TsvError


def _write_tsv(tmp_path: Path, filename: str, lines: list[str]) -> Path:
    p = tmp_path / filename
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


class TestTsvNumericCellCount:
    def test_all_numeric(self, tmp_path):
        p = _write_tsv(tmp_path, "nums.tsv", ["1\t2\t3", "4\t5\t6"])
        assert tsv_numeric_cell_count(p) == 6

    def test_mixed_numeric_and_string(self, tmp_path):
        p = _write_tsv(tmp_path, "mixed.tsv", ["name\tage\tcity", "Alice\t30\tLondon"])
        # "age" is string header, 30 is numeric; name/city are strings
        assert tsv_numeric_cell_count(p) == 1

    def test_all_strings(self, tmp_path):
        p = _write_tsv(tmp_path, "strs.tsv", ["foo\tbar", "baz\tqux"])
        assert tsv_numeric_cell_count(p) == 0

    def test_empty_cells_excluded(self, tmp_path):
        p = _write_tsv(tmp_path, "empties.tsv", ["\t\t", "1\t\t2"])
        # empty cells: not numeric; 1 and 2 are numeric
        assert tsv_numeric_cell_count(p) == 2

    def test_float_values(self, tmp_path):
        p = _write_tsv(tmp_path, "floats.tsv", ["3.14\t2.718", "-1.5\t0.0"])
        assert tsv_numeric_cell_count(p) == 4

    def test_negative_numbers(self, tmp_path):
        p = _write_tsv(tmp_path, "negs.tsv", ["-1\t-2\t-3"])
        assert tsv_numeric_cell_count(p) == 3

    def test_single_row_single_numeric(self, tmp_path):
        p = _write_tsv(tmp_path, "single.tsv", ["42"])
        assert tsv_numeric_cell_count(p) == 1

    def test_empty_file(self, tmp_path):
        p = _write_tsv(tmp_path, "empty.tsv", [""])
        assert tsv_numeric_cell_count(p) == 0

    def test_scientific_notation(self, tmp_path):
        p = _write_tsv(tmp_path, "sci.tsv", ["1e10\t2.5e-3"])
        assert tsv_numeric_cell_count(p) == 2

    def test_whitespace_padded_numeric(self, tmp_path):
        p = _write_tsv(tmp_path, "padded.tsv", [" 10 \t 20 "])
        # strip is applied before float conversion
        assert tsv_numeric_cell_count(p) == 2
