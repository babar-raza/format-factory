"""Tests for toml_to_gnumeric dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_TOML = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"
from toml.toml_to_gnumeric import toml_to_gnumeric


class TestTomlToGnumericBasic:
    def test_returns_entry_count(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = toml_to_gnumeric(MINIMAL_TOML, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        toml_to_gnumeric(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_produces_entries(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = toml_to_gnumeric(MINIMAL_TOML, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        toml_to_gnumeric(MINIMAL_TOML, dest)
        assert dest.stat().st_size > 0


class TestTomlToGnumericPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.gnumeric"
        toml_to_gnumeric(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = toml_to_gnumeric(str(MINIMAL_TOML), str(dest))
        assert isinstance(count, int) and dest.exists()
