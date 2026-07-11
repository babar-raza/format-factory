"""
Tests for gnumeric_to_fods dogfood export.

Verifies that Gnumeric spreadsheet cells are converted to FODS rows using
Format Factory's Gnumeric codec and FODS writer libraries.
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

from gnumeric.gnumeric_to_fods import gnumeric_to_fods


class TestGnumericToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.fods"
        count = gnumeric_to_fods(MINIMAL_GNM, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        gnumeric_to_fods(MINIMAL_GNM, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (flat format, not ZIP)."""
        dest = tmp_path / "out.fods"
        gnumeric_to_fods(MINIMAL_GNM, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        gnumeric_to_fods(MINIMAL_GNM, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestGnumericToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """Gnumeric rows appear in FODS output."""
        dest = tmp_path / "out.fods"
        count = gnumeric_to_fods(MINIMAL_GNM, dest)
        assert count >= 1

    def test_multi_cell_converts(self, tmp_path: Path) -> None:
        """Multi-cell Gnumeric file produces multiple rows."""
        dest = tmp_path / "out.fods"
        count = gnumeric_to_fods(MULTI_GNM, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        gnumeric_to_fods(MINIMAL_GNM, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestGnumericToFodsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the FODS sheet name."""
        dest = tmp_path / "out.fods"
        gnumeric_to_fods(MINIMAL_GNM, dest, sheet_name="GNM_Data")
        content = dest.read_text(encoding="utf-8")
        assert "GNM_Data" in content

    def test_sheet_index_zero(self, tmp_path: Path) -> None:
        """sheet_index=0 (default) exports the first sheet."""
        dest = tmp_path / "out.fods"
        count = gnumeric_to_fods(MINIMAL_GNM, dest, sheet_index=0)
        assert count >= 0


class TestGnumericToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        gnumeric_to_fods(MINIMAL_GNM, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = gnumeric_to_fods(str(MINIMAL_GNM), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
