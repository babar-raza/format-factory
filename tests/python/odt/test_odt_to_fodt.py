"""
Tests for odt_to_fodt dogfood export.

Verifies that ODT elements are converted to FODT blocks using
Format Factory's ODT parser and FODT writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
TWO_PARA_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "two-paragraphs.odt"

from odt.odt_to_fodt import odt_to_fodt


class TestOdtToFodtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = odt_to_fodt(MINIMAL_ODT, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        odt_to_fodt(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        odt_to_fodt(MINIMAL_ODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_paragraph(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        odt_to_fodt(MINIMAL_ODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "text:p" in content


class TestOdtToFodtContent:
    """Content correctness tests."""

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = odt_to_fodt(MINIMAL_ODT, dest)
        assert count >= 1

    def test_two_paragraphs_convert(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = odt_to_fodt(TWO_PARA_ODT, dest)
        assert dest.exists() and count >= 2

    def test_skip_empty_default(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = odt_to_fodt(MINIMAL_ODT, dest, skip_empty=True)
        assert count >= 0


class TestOdtToFodtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.fodt"
        odt_to_fodt(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = odt_to_fodt(str(MINIMAL_ODT), str(dest))
        assert isinstance(count, int) and dest.exists()
