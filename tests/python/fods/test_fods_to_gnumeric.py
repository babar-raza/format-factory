"""Tests for fods_to_gnumeric dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
from fods.fods_to_gnumeric import fods_to_gnumeric


class TestFodsToGnumericBasic:
    def test_returns_row_count(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fods_to_gnumeric(MINIMAL_FODS, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        fods_to_gnumeric(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fods_to_gnumeric(MINIMAL_FODS, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        fods_to_gnumeric(MINIMAL_FODS, dest)
        assert dest.stat().st_size > 0


class TestFodsToGnumericPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.gnumeric"
        fods_to_gnumeric(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fods_to_gnumeric(str(MINIMAL_FODS), str(dest))
        assert isinstance(count, int) and dest.exists()
