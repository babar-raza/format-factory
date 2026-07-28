"""Tests for csv_duplicate_row_count — counts duplicate rows in CSV files."""

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import csv_duplicate_row_count


def _write_csv(tmp_path, content: str) -> Path:
    p = tmp_path / "test.csv"
    p.write_bytes(content.encode("utf-8"))
    return p


class TestNoDuplicates:
    def test_unique_rows(self, tmp_path):
        p = _write_csv(tmp_path, "a,b\n1,2\n3,4\n5,6\n")
        assert csv_duplicate_row_count(p) == 0

    def test_single_row(self, tmp_path):
        p = _write_csv(tmp_path, "a,b\n1,2\n")
        assert csv_duplicate_row_count(p) == 0

    def test_empty_file(self, tmp_path):
        p = _write_csv(tmp_path, "")
        assert csv_duplicate_row_count(p) == 0


class TestWithDuplicates:
    def test_one_duplicate_pair(self, tmp_path):
        p = _write_csv(tmp_path, "a,b\n1,2\n1,2\n")
        assert csv_duplicate_row_count(p) == 1

    def test_triple_duplicate(self, tmp_path):
        p = _write_csv(tmp_path, "a,b\n1,2\n1,2\n1,2\n")
        assert csv_duplicate_row_count(p) == 2

    def test_multiple_duplicate_groups(self, tmp_path):
        p = _write_csv(tmp_path, "x\nA\nB\nA\nB\nC\n")
        assert csv_duplicate_row_count(p) == 2

    def test_all_identical(self, tmp_path):
        p = _write_csv(tmp_path, "v\n1\n1\n1\n1\n")
        assert csv_duplicate_row_count(p) == 3


class TestEdgeCases:
    def test_header_only(self, tmp_path):
        p = _write_csv(tmp_path, "a,b,c\n")
        assert csv_duplicate_row_count(p) == 0

    def test_whitespace_matters(self, tmp_path):
        p = _write_csv(tmp_path, "v\n a\na\n")
        # " a" != "a" — not duplicates
        assert csv_duplicate_row_count(p) == 0

    def test_return_type(self, tmp_path):
        p = _write_csv(tmp_path, "a\n1\n")
        assert isinstance(csv_duplicate_row_count(p), int)
