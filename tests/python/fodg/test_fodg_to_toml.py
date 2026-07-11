"""
Tests for fodg_to_toml dogfood export.

Verifies that FODG pages are converted to TOML array table entries using
Format Factory's FODG codec and TOML writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODG = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"

from fodg.fodg_to_toml import fodg_to_toml


class TestFodgToTomlBasic:
    """Basic conversion tests."""

    def test_returns_page_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = fodg_to_toml(MINIMAL_FODG, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        fodg_to_toml(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_produces_pages(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = fodg_to_toml(MINIMAL_FODG, dest)
        assert count >= 1

    def test_contains_pages_key(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        fodg_to_toml(MINIMAL_FODG, dest)
        content = dest.read_text(encoding="utf-8")
        assert "pages" in content

    def test_custom_table_key(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        fodg_to_toml(MINIMAL_FODG, dest, table_key="data")
        content = dest.read_text(encoding="utf-8")
        assert "data" in content


class TestFodgToTomlPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.toml"
        fodg_to_toml(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = fodg_to_toml(str(MINIMAL_FODG), str(dest))
        assert isinstance(count, int) and dest.exists()
