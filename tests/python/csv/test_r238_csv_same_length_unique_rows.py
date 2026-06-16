"""Tests for csv_all_rows_same_length and csv_unique_row_count (Sprint 28)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from src.python.csv.csv_parser import csv_all_rows_same_length, csv_unique_row_count


def _write(tmp_path, name, content):
    p = tmp_path / f"{name}.csv"
    p.write_text(content, encoding="utf-8")
    return str(p)


class TestCsvAllRowsSameLength:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt", "h1,h2\na,b\nc,d\n")
        assert isinstance(csv_all_rows_same_length(p), bool)

    def test_uniform_columns(self, tmp_path):
        # header row + 2 data rows all with 3 fields
        p = _write(tmp_path, "uc", "a,b,c\n1,2,3\n4,5,6\n")
        assert csv_all_rows_same_length(p) is True

    def test_empty_file(self, tmp_path):
        # empty CSV => True (vacuous)
        p = _write(tmp_path, "ef", "")
        assert csv_all_rows_same_length(p) is True

    def test_single_data_row(self, tmp_path):
        p = _write(tmp_path, "sd", "h\nval\n")
        assert csv_all_rows_same_length(p) is True

    def test_two_identical_length_rows(self, tmp_path):
        p = _write(tmp_path, "ti", "x,y\na,b\nc,d\n")
        assert csv_all_rows_same_length(p) is True


class TestCsvUniqueRowCount:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, "rt2", "a\nb\nc\n")
        assert isinstance(csv_unique_row_count(p), int)

    def test_all_unique_rows(self, tmp_path):
        # 3 fully distinct rows => 3 unique
        p = _write(tmp_path, "au", "a\nb\nc\n")
        assert csv_unique_row_count(p) == 3

    def test_duplicate_reduces_count(self, tmp_path):
        # 4 rows, row "foo" repeated => 3 unique
        p = _write(tmp_path, "ec", "col\nfoo\nfoo\nbar\n")
        assert csv_unique_row_count(p) == 3

    def test_nonnegative(self, tmp_path):
        p = _write(tmp_path, "nn", "x\n1\n2\n")
        assert csv_unique_row_count(p) >= 0

    def test_single_row(self, tmp_path):
        # single row => 1 unique
        p = _write(tmp_path, "sr", "only\n")
        assert csv_unique_row_count(p) == 1
