"""
Tests for gnumeric_to_toml dogfood export.

Verifies that Gnumeric rows are converted to TOML array table entries using
Format Factory's Gnumeric codec and TOML writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"

from gnumeric.gnumeric_to_toml import gnumeric_to_toml


class TestGnumericToTomlBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = gnumeric_to_toml(MINIMAL_GNUMERIC, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        gnumeric_to_toml(MINIMAL_GNUMERIC, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = gnumeric_to_toml(MINIMAL_GNUMERIC, dest)
        assert count >= 1

    def test_custom_table_key(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        gnumeric_to_toml(MINIMAL_GNUMERIC, dest, table_key="data")
        content = dest.read_text(encoding="utf-8")
        assert "data" in content


class TestGnumericToTomlPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.toml"
        gnumeric_to_toml(MINIMAL_GNUMERIC, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = gnumeric_to_toml(str(MINIMAL_GNUMERIC), str(dest))
        assert isinstance(count, int) and dest.exists()
