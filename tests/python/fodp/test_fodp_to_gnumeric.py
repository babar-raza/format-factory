"""Tests for fodp_to_gnumeric dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
from fodp.fodp_to_gnumeric import fodp_to_gnumeric


class TestFodpToGnumericBasic:
    def test_returns_slide_count(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fodp_to_gnumeric(MINIMAL_FODP, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        fodp_to_gnumeric(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_produces_slides(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fodp_to_gnumeric(MINIMAL_FODP, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        fodp_to_gnumeric(MINIMAL_FODP, dest)
        assert dest.stat().st_size > 0


class TestFodpToGnumericPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.gnumeric"
        fodp_to_gnumeric(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = fodp_to_gnumeric(str(MINIMAL_FODP), str(dest))
        assert isinstance(count, int) and dest.exists()
