"""Tests for ods_to_dif dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
from src.python.ods.ods_to_dif import ods_to_dif


class TestOdsToDifBasic:
    def test_returns_row_count(self, tmp_path):
        dest = tmp_path / "out.dif"
        count = ods_to_dif(MINIMAL_ODS, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.dif"
        ods_to_dif(MINIMAL_ODS, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path):
        dest = tmp_path / "out.dif"
        count = ods_to_dif(MINIMAL_ODS, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.dif"
        ods_to_dif(MINIMAL_ODS, dest)
        assert dest.stat().st_size > 0


class TestOdsToDifPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.dif"
        ods_to_dif(MINIMAL_ODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.dif"
        count = ods_to_dif(str(MINIMAL_ODS), str(dest))
        assert isinstance(count, int) and dest.exists()
