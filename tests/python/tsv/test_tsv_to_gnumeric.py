"""Tests for tsv_to_gnumeric dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
from tsv.tsv_to_gnumeric import tsv_to_gnumeric


class TestTsvToGnumericBasic:
    def test_returns_row_count(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = tsv_to_gnumeric(MINIMAL_TSV, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        tsv_to_gnumeric(MINIMAL_TSV, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = tsv_to_gnumeric(MINIMAL_TSV, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        tsv_to_gnumeric(MINIMAL_TSV, dest)
        assert dest.stat().st_size > 0


class TestTsvToGnumericPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.gnumeric"
        tsv_to_gnumeric(MINIMAL_TSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = tsv_to_gnumeric(str(MINIMAL_TSV), str(dest))
        assert isinstance(count, int) and dest.exists()
