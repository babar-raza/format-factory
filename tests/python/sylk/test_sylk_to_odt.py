"""
Tests for sylk_to_odt dogfood export.

Verifies that SYLK rows are converted to ODT paragraphs using
Format Factory's SYLK parser and ODT writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
NUMERIC_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk"

from sylk.sylk_to_odt import sylk_to_odt


class TestSylkToOdtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of paragraphs written."""
        dest = tmp_path / "out.odt"
        count = sylk_to_odt(MINIMAL_SYLK, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .odt file is created at the specified path."""
        dest = tmp_path / "out.odt"
        sylk_to_odt(MINIMAL_SYLK, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODT file is a valid ZIP container."""
        dest = tmp_path / "out.odt"
        sylk_to_odt(MINIMAL_SYLK, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODT ZIP contains content.xml."""
        dest = tmp_path / "out.odt"
        sylk_to_odt(MINIMAL_SYLK, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestSylkToOdtContent:
    """Content correctness tests."""

    def test_content_xml_has_paragraph(self, tmp_path: Path) -> None:
        """content.xml contains paragraph elements."""
        dest = tmp_path / "out.odt"
        sylk_to_odt(MINIMAL_SYLK, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "text:p" in content

    def test_two_rows_from_2x2(self, tmp_path: Path) -> None:
        """minimal-2x2.slk produces 2 paragraphs."""
        dest = tmp_path / "out.odt"
        count = sylk_to_odt(MINIMAL_SYLK, dest)
        assert count == 2

    def test_numeric_row_converts(self, tmp_path: Path) -> None:
        """Numeric SYLK row converts without error."""
        dest = tmp_path / "out.odt"
        count = sylk_to_odt(NUMERIC_SYLK, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """content.xml has substantial content."""
        dest = tmp_path / "out.odt"
        sylk_to_odt(MINIMAL_SYLK, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestSylkToOdtOptions:
    """Option flag tests."""

    def test_custom_separator(self, tmp_path: Path) -> None:
        """Custom separator joins cell values in paragraphs."""
        dest = tmp_path / "out.odt"
        sylk_to_odt(MINIMAL_SYLK, dest, separator=" | ")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert " | " in content


class TestSylkToOdtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.odt"
        sylk_to_odt(MINIMAL_SYLK, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.odt"
        count = sylk_to_odt(str(MINIMAL_SYLK), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
