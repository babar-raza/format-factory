"""
Tests for abw_to_toml dogfood export.

Verifies that ABW paragraphs are converted to TOML array table entries using
Format Factory's ABW codec and TOML writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
TWO_PARA_ABW = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"

from abw.abw_to_toml import abw_to_toml


class TestAbwToTomlBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = abw_to_toml(MINIMAL_ABW, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        abw_to_toml(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_produces_entries(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = abw_to_toml(MINIMAL_ABW, dest)
        assert count >= 1

    def test_two_paragraphs(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = abw_to_toml(TWO_PARA_ABW, dest)
        assert count >= 2

    def test_contains_paragraph_key(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        abw_to_toml(MINIMAL_ABW, dest)
        content = dest.read_text(encoding="utf-8")
        assert "paragraphs" in content


class TestAbwToTomlPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.toml"
        abw_to_toml(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = abw_to_toml(str(MINIMAL_ABW), str(dest))
        assert isinstance(count, int) and dest.exists()
