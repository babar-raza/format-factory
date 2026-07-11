"""Tests for odt_to_gnumeric dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
from odt.odt_to_gnumeric import odt_to_gnumeric


class TestOdtToGnumericBasic:
    def test_returns_element_count(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = odt_to_gnumeric(MINIMAL_ODT, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        odt_to_gnumeric(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_produces_elements(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = odt_to_gnumeric(MINIMAL_ODT, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        odt_to_gnumeric(MINIMAL_ODT, dest)
        assert dest.stat().st_size > 0


class TestOdtToGnumericPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.gnumeric"
        odt_to_gnumeric(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = odt_to_gnumeric(str(MINIMAL_ODT), str(dest))
        assert isinstance(count, int) and dest.exists()
