"""
Tests for gnumeric_to_fodt dogfood export.

Verifies that Gnumeric spreadsheet rows are converted to FODT paragraphs using
Format Factory's Gnumeric codec and FODT writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_GNM = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
MULTI_GNM = _REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric"

from gnumeric.gnumeric_to_fodt import gnumeric_to_fodt


class TestGnumericToFodtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = gnumeric_to_fodt(MINIMAL_GNM, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        gnumeric_to_fodt(MINIMAL_GNM, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        gnumeric_to_fodt(MINIMAL_GNM, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_paragraph(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        gnumeric_to_fodt(MINIMAL_GNM, dest)
        content = dest.read_text(encoding="utf-8")
        assert "text:p" in content


class TestGnumericToFodtContent:
    """Content correctness tests."""

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = gnumeric_to_fodt(MINIMAL_GNM, dest)
        assert count >= 1

    def test_multi_cell_converts(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = gnumeric_to_fodt(MULTI_GNM, dest)
        assert dest.exists() and count >= 1

    def test_custom_separator(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        gnumeric_to_fodt(MULTI_GNM, dest, separator=" , ")
        content = dest.read_text(encoding="utf-8")
        assert " , " in content


class TestGnumericToFodtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.fodt"
        gnumeric_to_fodt(MINIMAL_GNM, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = gnumeric_to_fodt(str(MINIMAL_GNM), str(dest))
        assert isinstance(count, int) and dest.exists()
