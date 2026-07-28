"""Tests for csv_empty_cell_count function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import csv_empty_cell_count


def _write_csv(tmp_path, content, name="test.csv"):
    p = tmp_path / name
    p.write_bytes(content.encode("utf-8"))
    return str(p)


class TestCsvEmptyCellCount:
    def test_no_empty_cells(self, tmp_path):
        path = _write_csv(tmp_path, "a,b\n1,2\n3,4\n")
        assert csv_empty_cell_count(path) == 0

    def test_some_empty(self, tmp_path):
        path = _write_csv(tmp_path, "a,b\n1,\n,4\n")
        assert csv_empty_cell_count(path) == 2

    def test_all_empty(self, tmp_path):
        path = _write_csv(tmp_path, "a,b\n,\n,\n")
        assert csv_empty_cell_count(path) == 4

    def test_single_row_no_empty(self, tmp_path):
        path = _write_csv(tmp_path, "x,y\n1,2\n")
        assert csv_empty_cell_count(path) == 0

    def test_whitespace_is_empty(self, tmp_path):
        path = _write_csv(tmp_path, "a,b\n , \n")
        assert csv_empty_cell_count(path) == 2

    def test_empty_file_no_data(self, tmp_path):
        path = _write_csv(tmp_path, "a,b\n")
        assert csv_empty_cell_count(path) == 0

    def test_return_type(self, tmp_path):
        path = _write_csv(tmp_path, "a\n1\n")
        assert isinstance(csv_empty_cell_count(path), int)

    def test_importable_from_package(self):
        from src.python.ff_csv.csv_parser import csv_empty_cell_count as fn
        assert callable(fn)
