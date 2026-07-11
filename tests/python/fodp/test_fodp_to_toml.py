"""
Tests for fodp_to_toml dogfood export.

Verifies that FODP slides are converted to TOML array table entries using
Format Factory's FODP codec and TOML writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"

from fodp.fodp_to_toml import fodp_to_toml


class TestFodpToTomlBasic:
    """Basic conversion tests."""

    def test_returns_slide_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = fodp_to_toml(MINIMAL_FODP, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        fodp_to_toml(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_produces_slides(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = fodp_to_toml(MINIMAL_FODP, dest)
        assert count >= 1

    def test_contains_slides_key(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        fodp_to_toml(MINIMAL_FODP, dest)
        content = dest.read_text(encoding="utf-8")
        assert "slides" in content

    def test_custom_table_key(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        fodp_to_toml(MINIMAL_FODP, dest, table_key="data")
        content = dest.read_text(encoding="utf-8")
        assert "data" in content


class TestFodpToTomlPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.toml"
        fodp_to_toml(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = fodp_to_toml(str(MINIMAL_FODP), str(dest))
        assert isinstance(count, int) and dest.exists()
