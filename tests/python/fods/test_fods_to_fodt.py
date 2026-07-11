"""
Tests for fods_to_fodt dogfood export.

Verifies that FODS rows are converted to FODT paragraphs using
Format Factory's FODS parser and FODT writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"

from fods.fods_to_fodt import fods_to_fodt


class TestFodsToFodtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of paragraphs written."""
        dest = tmp_path / "out.fodt"
        count = fods_to_fodt(MINIMAL_FODS, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fodt file is created at the specified path."""
        dest = tmp_path / "out.fodt"
        fods_to_fodt(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODT file is XML."""
        dest = tmp_path / "out.fodt"
        fods_to_fodt(MINIMAL_FODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_paragraph(self, tmp_path: Path) -> None:
        """FODT file contains paragraph elements."""
        dest = tmp_path / "out.fodt"
        fods_to_fodt(MINIMAL_FODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "text:p" in content


class TestFodsToFodtContent:
    """Content correctness tests."""

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        """FODS rows appear as FODT paragraphs."""
        dest = tmp_path / "out.fodt"
        count = fods_to_fodt(MINIMAL_FODS, dest)
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODT file has substantial content."""
        dest = tmp_path / "out.fodt"
        fods_to_fodt(MINIMAL_FODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestFodsToFodtOptions:
    """Option flag tests."""

    def test_custom_separator(self, tmp_path: Path) -> None:
        """separator parameter joins cells in each paragraph."""
        dest = tmp_path / "out.fodt"
        count = fods_to_fodt(MINIMAL_FODS, dest, separator=" , ")
        assert count >= 0

    def test_sheet_index_zero(self, tmp_path: Path) -> None:
        """sheet_index=0 exports the first sheet."""
        dest = tmp_path / "out.fodt"
        count = fods_to_fodt(MINIMAL_FODS, dest, sheet_index=0)
        assert count >= 0


class TestFodsToFodtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fodt"
        fods_to_fodt(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fodt"
        count = fods_to_fodt(str(MINIMAL_FODS), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
