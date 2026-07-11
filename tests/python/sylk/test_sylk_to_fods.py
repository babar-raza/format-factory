"""
Tests for sylk_to_fods dogfood export.

Verifies that SYLK grid cells are converted to FODS rows using
Format Factory's SYLK parser and FODS writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_SLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
NUMERIC_SLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk"

from sylk.sylk_to_fods import sylk_to_fods


class TestSylkToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.fods"
        count = sylk_to_fods(MINIMAL_SLK, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        sylk_to_fods(MINIMAL_SLK, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (flat format, not ZIP)."""
        dest = tmp_path / "out.fods"
        sylk_to_fods(MINIMAL_SLK, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        sylk_to_fods(MINIMAL_SLK, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestSylkToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """SYLK rows appear in FODS output."""
        dest = tmp_path / "out.fods"
        count = sylk_to_fods(MINIMAL_SLK, dest)
        assert count >= 1

    def test_numeric_sylk_converts(self, tmp_path: Path) -> None:
        """Numeric SYLK file converts without error."""
        dest = tmp_path / "out.fods"
        count = sylk_to_fods(NUMERIC_SLK, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        sylk_to_fods(MINIMAL_SLK, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestSylkToFodsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the FODS sheet name."""
        dest = tmp_path / "out.fods"
        sylk_to_fods(MINIMAL_SLK, dest, sheet_name="SYLK_Data")
        content = dest.read_text(encoding="utf-8")
        assert "SYLK_Data" in content


class TestSylkToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        sylk_to_fods(MINIMAL_SLK, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = sylk_to_fods(str(MINIMAL_SLK), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
