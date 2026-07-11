"""
Tests for odt_to_fods dogfood export.

Verifies that ODT document elements are converted to FODS rows using
Format Factory's ODT parser and FODS writer libraries.
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

from odt.odt_to_fods import odt_to_fods


class TestOdtToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.fods"
        count = odt_to_fods(MINIMAL_ODT, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        odt_to_fods(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (flat format, not ZIP)."""
        dest = tmp_path / "out.fods"
        odt_to_fods(MINIMAL_ODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        odt_to_fods(MINIMAL_ODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestOdtToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """ODT paragraphs appear as FODS rows."""
        dest = tmp_path / "out.fods"
        count = odt_to_fods(MINIMAL_ODT, dest)
        assert count >= 1

    def test_two_paragraphs_convert(self, tmp_path: Path) -> None:
        """Two-paragraph ODT produces at least 2 data rows."""
        dest = tmp_path / "out.fods"
        count = odt_to_fods(TWO_PARA_ODT, dest)
        assert dest.exists()
        assert count >= 2

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        odt_to_fods(MINIMAL_ODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestOdtToFodsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the FODS sheet name."""
        dest = tmp_path / "out.fods"
        odt_to_fods(MINIMAL_ODT, dest, sheet_name="ODT_Data")
        content = dest.read_text(encoding="utf-8")
        assert "ODT_Data" in content

    def test_include_header(self, tmp_path: Path) -> None:
        """include_header=True writes element_type header."""
        dest = tmp_path / "out.fods"
        odt_to_fods(MINIMAL_ODT, dest, include_header=True)
        content = dest.read_text(encoding="utf-8")
        assert "element_type" in content

    def test_no_header(self, tmp_path: Path) -> None:
        """include_header=False omits the header row."""
        dest = tmp_path / "out.fods"
        count = odt_to_fods(MINIMAL_ODT, dest, include_header=False)
        assert count >= 0


class TestOdtToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        odt_to_fods(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = odt_to_fods(str(MINIMAL_ODT), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
