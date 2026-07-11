"""Tests for fodg_to_gnumeric dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODG = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
from fodg.fodg_to_gnumeric import fodg_to_gnumeric


class TestFodgToGnumericBasic:
    def test_returns_page_count(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fodg_to_gnumeric(MINIMAL_FODG, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        fodg_to_gnumeric(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_produces_pages(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fodg_to_gnumeric(MINIMAL_FODG, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        fodg_to_gnumeric(MINIMAL_FODG, dest)
        assert dest.stat().st_size > 0


class TestFodgToGnumericPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.gnumeric"
        fodg_to_gnumeric(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fodg_to_gnumeric(str(MINIMAL_FODG), str(dest))
        assert isinstance(count, int) and dest.exists()
