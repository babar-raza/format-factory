"""Tests for product deepening: CSV + PBM new analytics functions.

Sprint: PRODUCT-DEEPENING-SPRINT9-20260616
Adds: csv_distinct_value_count, csv_empty_cell_ratio,
      pbm_black_pixel_count, pbm_is_uniform
"""
import os
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))


def _first_pbm():
    files = sorted((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm"))
    assert files, "No PBM samples"
    return str(files[0])


# --- CSV ---

class TestCsvDistinctValueCount:
    def test_returns_int(self, tmp_path):
        from src.python.csv.csv_parser import csv_distinct_value_count
        p = str(tmp_path / "test.csv")
        Path(p).write_text("a,b\n1,2\n1,3\n", encoding="utf-8")
        assert isinstance(csv_distinct_value_count(p), int)

    def test_correct_count(self, tmp_path):
        from src.python.csv.csv_parser import csv_distinct_value_count
        p = str(tmp_path / "test.csv")
        Path(p).write_text("h1,h2\nA,B\nA,C\nD,B\n", encoding="utf-8")
        # Values: h1, h2, A, B, A, C, D, B -> distinct: h1, h2, A, B, C, D = 6
        assert csv_distinct_value_count(p) == 6

    def test_empty_file(self, tmp_path):
        from src.python.csv.csv_parser import csv_distinct_value_count
        p = str(tmp_path / "empty.csv")
        Path(p).write_text("", encoding="utf-8")
        assert csv_distinct_value_count(p) == 0


class TestCsvEmptyCellRatio:
    def test_returns_float(self, tmp_path):
        from src.python.csv.csv_parser import csv_empty_cell_ratio
        p = str(tmp_path / "test.csv")
        Path(p).write_text("a,b\n1,2\n", encoding="utf-8")
        assert isinstance(csv_empty_cell_ratio(p), float)

    def test_no_empty_cells(self, tmp_path):
        from src.python.csv.csv_parser import csv_empty_cell_ratio
        p = str(tmp_path / "full.csv")
        Path(p).write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
        assert csv_empty_cell_ratio(p) == 0.0

    def test_some_empty(self, tmp_path):
        from src.python.csv.csv_parser import csv_empty_cell_ratio
        p = str(tmp_path / "sparse.csv")
        Path(p).write_text("a,b\n1,\n,4\n", encoding="utf-8")
        ratio = csv_empty_cell_ratio(p)
        assert 0.0 < ratio < 1.0

    def test_range(self, tmp_path):
        from src.python.csv.csv_parser import csv_empty_cell_ratio
        p = str(tmp_path / "test.csv")
        Path(p).write_text("a,b\n1,2\n", encoding="utf-8")
        ratio = csv_empty_cell_ratio(p)
        assert 0.0 <= ratio <= 1.0


# --- PBM ---

class TestPbmBlackPixelCount:
    def test_returns_int(self):
        from pbm import pbm_black_pixel_count
        assert isinstance(pbm_black_pixel_count(_first_pbm()), int)

    def test_nonnegative(self):
        from pbm import pbm_black_pixel_count
        assert pbm_black_pixel_count(_first_pbm()) >= 0

    def test_at_most_total(self):
        from pbm import pbm_black_pixel_count, pbm_total_pixel_count
        path = _first_pbm()
        assert pbm_black_pixel_count(path) <= pbm_total_pixel_count(path)

    def test_consistent_with_ratio(self):
        from pbm import pbm_black_pixel_count, pbm_total_pixel_count, pbm_black_pixel_ratio
        path = _first_pbm()
        total = pbm_total_pixel_count(path)
        if total > 0:
            expected_ratio = pbm_black_pixel_count(path) / total
            assert abs(expected_ratio - pbm_black_pixel_ratio(path)) < 0.01


class TestPbmIsUniform:
    def test_returns_bool(self):
        from pbm import pbm_is_uniform
        assert isinstance(pbm_is_uniform(_first_pbm()), bool)

    def test_consistent_with_all_white_black(self):
        from pbm import pbm_is_uniform, pbm_all_white, pbm_all_black
        path = _first_pbm()
        if pbm_all_white(path) or pbm_all_black(path):
            assert pbm_is_uniform(path) is True
