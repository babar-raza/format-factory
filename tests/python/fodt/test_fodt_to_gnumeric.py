"""Tests for fodt_to_gnumeric dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODT = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
from fodt.fodt_to_gnumeric import fodt_to_gnumeric


class TestFodtToGnumericBasic:
    def test_returns_block_count(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fodt_to_gnumeric(MINIMAL_FODT, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        fodt_to_gnumeric(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_produces_blocks(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fodt_to_gnumeric(MINIMAL_FODT, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        fodt_to_gnumeric(MINIMAL_FODT, dest)
        assert dest.stat().st_size > 0


class TestFodtToGnumericPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.gnumeric"
        fodt_to_gnumeric(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fodt_to_gnumeric(str(MINIMAL_FODT), str(dest))
        assert isinstance(count, int) and dest.exists()
