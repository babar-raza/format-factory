"""
Tests for gnumeric_to_odt dogfood export.

Verifies that Gnumeric spreadsheet rows are converted to ODT paragraphs using
Format Factory's Gnumeric codec and ODT writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_GNM = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
MULTI_GNM = _REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric"

from gnumeric.gnumeric_to_odt import gnumeric_to_odt


class TestGnumericToOdtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of paragraphs written."""
        dest = tmp_path / "out.odt"
        count = gnumeric_to_odt(MINIMAL_GNM, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .odt file is created at the specified path."""
        dest = tmp_path / "out.odt"
        gnumeric_to_odt(MINIMAL_GNM, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODT file is a valid ZIP container."""
        dest = tmp_path / "out.odt"
        gnumeric_to_odt(MINIMAL_GNM, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODT ZIP contains content.xml."""
        dest = tmp_path / "out.odt"
        gnumeric_to_odt(MINIMAL_GNM, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestGnumericToOdtContent:
    """Content correctness tests."""

    def test_content_xml_has_paragraph(self, tmp_path: Path) -> None:
        """content.xml contains paragraph elements."""
        dest = tmp_path / "out.odt"
        gnumeric_to_odt(MINIMAL_GNM, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "text:p" in content

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        """Gnumeric rows produce ODT paragraphs."""
        dest = tmp_path / "out.odt"
        count = gnumeric_to_odt(MINIMAL_GNM, dest)
        assert count >= 1

    def test_multi_cell_converts(self, tmp_path: Path) -> None:
        """Multi-cell Gnumeric file converts without error."""
        dest = tmp_path / "out.odt"
        count = gnumeric_to_odt(MULTI_GNM, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """content.xml has substantial content."""
        dest = tmp_path / "out.odt"
        gnumeric_to_odt(MINIMAL_GNM, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestGnumericToOdtOptions:
    """Option flag tests."""

    def test_custom_separator(self, tmp_path: Path) -> None:
        """Custom separator joins cell values in paragraphs."""
        dest = tmp_path / "out.odt"
        # Use multi-cell sample so separator appears between columns
        gnumeric_to_odt(MULTI_GNM, dest, separator=" | ")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert " | " in content

    def test_include_row_index(self, tmp_path: Path) -> None:
        """include_row_index=True prepends row number to each paragraph."""
        dest = tmp_path / "out.odt"
        gnumeric_to_odt(MINIMAL_GNM, dest, include_row_index=True)
        assert dest.exists()

    def test_sheet_index_default(self, tmp_path: Path) -> None:
        """Default sheet_index=0 exports the first sheet."""
        dest = tmp_path / "out.odt"
        count = gnumeric_to_odt(MINIMAL_GNM, dest, sheet_index=0)
        assert count >= 0


class TestGnumericToOdtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.odt"
        gnumeric_to_odt(MINIMAL_GNM, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.odt"
        count = gnumeric_to_odt(str(MINIMAL_GNM), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
