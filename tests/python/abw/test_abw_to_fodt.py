"""
Tests for abw_to_fodt dogfood export.

Verifies that ABW paragraphs are converted to FODT paragraphs using
Format Factory's ABW codec and FODT writer libraries.
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

from abw.abw_to_fodt import abw_to_fodt


class TestAbwToFodtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = abw_to_fodt(MINIMAL_ABW, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        abw_to_fodt(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        abw_to_fodt(MINIMAL_ABW, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_paragraph(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        abw_to_fodt(MINIMAL_ABW, dest)
        content = dest.read_text(encoding="utf-8")
        assert "text:p" in content


class TestAbwToFodtContent:
    """Content correctness tests."""

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = abw_to_fodt(MINIMAL_ABW, dest)
        assert count >= 1

    def test_two_paragraphs_convert(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = abw_to_fodt(TWO_PARA_ABW, dest)
        assert dest.exists() and count >= 2

    def test_skip_empty_default(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = abw_to_fodt(MINIMAL_ABW, dest, skip_empty=True)
        assert count >= 0


class TestAbwToFodtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.fodt"
        abw_to_fodt(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = abw_to_fodt(str(MINIMAL_ABW), str(dest))
        assert isinstance(count, int) and dest.exists()
