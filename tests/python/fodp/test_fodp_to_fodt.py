"""
Tests for fodp_to_fodt dogfood export.

Verifies that FODP slides are converted to FODT paragraphs using
Format Factory's FODP codec and FODT writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
TWO_SLIDES = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"

from fodp.fodp_to_fodt import fodp_to_fodt


class TestFodpToFodtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodp_to_fodt(MINIMAL_FODP, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        fodp_to_fodt(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        fodp_to_fodt(MINIMAL_FODP, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_paragraph(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        fodp_to_fodt(MINIMAL_FODP, dest)
        content = dest.read_text(encoding="utf-8")
        assert "text:p" in content


class TestFodpToFodtContent:
    """Content correctness tests."""

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodp_to_fodt(MINIMAL_FODP, dest)
        assert count >= 1

    def test_two_slides_convert(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodp_to_fodt(TWO_SLIDES, dest)
        assert dest.exists() and count >= 2

    def test_custom_separator(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodp_to_fodt(MINIMAL_FODP, dest, separator=" | ")
        assert count >= 0


class TestFodpToFodtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.fodt"
        fodp_to_fodt(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = fodp_to_fodt(str(MINIMAL_FODP), str(dest))
        assert isinstance(count, int) and dest.exists()
