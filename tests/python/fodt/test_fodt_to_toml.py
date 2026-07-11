"""
Tests for fodt_to_toml dogfood export.

Verifies that FODT blocks are converted to TOML array table entries using
Format Factory's FODT parser and TOML writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODT = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"

from fodt.fodt_to_toml import fodt_to_toml


class TestFodtToTomlBasic:
    """Basic conversion tests."""

    def test_returns_block_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = fodt_to_toml(MINIMAL_FODT, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        fodt_to_toml(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_produces_blocks(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = fodt_to_toml(MINIMAL_FODT, dest)
        assert count >= 1

    def test_contains_block_type_key(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        fodt_to_toml(MINIMAL_FODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "block_type" in content

    def test_custom_table_key(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        fodt_to_toml(MINIMAL_FODT, dest, table_key="data")
        content = dest.read_text(encoding="utf-8")
        assert "data" in content


class TestFodtToTomlPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.toml"
        fodt_to_toml(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = fodt_to_toml(str(MINIMAL_FODT), str(dest))
        assert isinstance(count, int) and dest.exists()
