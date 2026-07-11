"""
Tests for fodg_to_fodt dogfood export.

Verifies that FODG pages are converted to FODT paragraphs using
Format Factory's FODG codec and FODT writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODG = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
SHAPES_FODG = _REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg"

from fodg.fodg_to_fodt import fodg_to_fodt


class TestFodgToFodtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodg_to_fodt(MINIMAL_FODG, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        fodg_to_fodt(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        fodg_to_fodt(MINIMAL_FODG, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_paragraph(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        fodg_to_fodt(MINIMAL_FODG, dest)
        content = dest.read_text(encoding="utf-8")
        assert "text:p" in content


class TestFodgToFodtContent:
    """Content correctness tests."""

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodg_to_fodt(MINIMAL_FODG, dest)
        assert count >= 1

    def test_shapes_fodg_converts(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodg_to_fodt(SHAPES_FODG, dest)
        assert dest.exists() and count >= 1

    def test_custom_separator(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodg_to_fodt(MINIMAL_FODG, dest, separator=" | ")
        assert count >= 0


class TestFodgToFodtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.fodt"
        fodg_to_fodt(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodg_to_fodt(str(MINIMAL_FODG), str(dest))
        assert isinstance(count, int) and dest.exists()
