"""Tests for tsv_duplicate_row_count — counts duplicate rows in TSV files."""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import tsv_duplicate_row_count


def _write_tsv(tmp_path, content: str) -> Path:
    p = tmp_path / "test.tsv"
    p.write_bytes(content.encode("utf-8"))
    return p


class TestNoDuplicates:
    def test_unique_rows(self, tmp_path):
        p = _write_tsv(tmp_path, "a\tb\n1\t2\n3\t4\n5\t6\n")
        assert tsv_duplicate_row_count(p) == 0

    def test_single_row(self, tmp_path):
        p = _write_tsv(tmp_path, "a\tb\n1\t2\n")
        assert tsv_duplicate_row_count(p) == 0

    def test_empty_file(self, tmp_path):
        p = _write_tsv(tmp_path, "")
        assert tsv_duplicate_row_count(p) == 0


class TestWithDuplicates:
    def test_one_duplicate_pair(self, tmp_path):
        p = _write_tsv(tmp_path, "a\tb\n1\t2\n1\t2\n")
        assert tsv_duplicate_row_count(p) == 1

    def test_triple_duplicate(self, tmp_path):
        p = _write_tsv(tmp_path, "a\tb\n1\t2\n1\t2\n1\t2\n")
        assert tsv_duplicate_row_count(p) == 2

    def test_multiple_groups(self, tmp_path):
        p = _write_tsv(tmp_path, "x\nA\nB\nA\nB\nC\n")
        assert tsv_duplicate_row_count(p) == 2

    def test_all_identical(self, tmp_path):
        p = _write_tsv(tmp_path, "v\n1\n1\n1\n1\n")
        assert tsv_duplicate_row_count(p) == 3


class TestEdgeCases:
    def test_return_type(self, tmp_path):
        p = _write_tsv(tmp_path, "a\n1\n")
        assert isinstance(tsv_duplicate_row_count(p), int)

    def test_header_only(self, tmp_path):
        p = _write_tsv(tmp_path, "a\tb\tc\n")
        assert tsv_duplicate_row_count(p) == 0
