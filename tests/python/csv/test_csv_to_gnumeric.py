"""Tests for csv_to_gnumeric dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
from src.python.csv.csv_to_gnumeric import csv_to_gnumeric


class TestCsvToGnumericBasic:
    def test_returns_row_count(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = csv_to_gnumeric(MINIMAL_CSV, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        csv_to_gnumeric(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = csv_to_gnumeric(MINIMAL_CSV, dest)
        assert count >= 1

    def test_output_is_binary(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        csv_to_gnumeric(MINIMAL_CSV, dest)
        assert dest.stat().st_size > 0


class TestCsvToGnumericPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.gnumeric"
        csv_to_gnumeric(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = csv_to_gnumeric(str(MINIMAL_CSV), str(dest))
        assert isinstance(count, int) and dest.exists()
