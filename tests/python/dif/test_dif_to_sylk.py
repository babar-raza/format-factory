"""Tests for dif_to_sylk dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
from src.python.dif.dif_to_sylk import dif_to_sylk


class TestDifToSylkBasic:
    def test_returns_row_count(self, tmp_path):
        dest = tmp_path / "out.slk"
        count = dif_to_sylk(MINIMAL_DIF, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.slk"
        dif_to_sylk(MINIMAL_DIF, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path):
        dest = tmp_path / "out.slk"
        count = dif_to_sylk(MINIMAL_DIF, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.slk"
        dif_to_sylk(MINIMAL_DIF, dest)
        assert dest.stat().st_size > 0


class TestDifToSylkPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.slk"
        dif_to_sylk(MINIMAL_DIF, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.slk"
        count = dif_to_sylk(str(MINIMAL_DIF), str(dest))
        assert isinstance(count, int) and dest.exists()
