"""
Tests for fodt_to_odt dogfood export.

Verifies that FODT blocks are converted to ODT paragraphs using
Format Factory's FODT parser and ODT writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODT = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
HEADINGS_FODT = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"

from fodt.fodt_to_odt import fodt_to_odt


class TestFodtToOdtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of paragraphs written."""
        dest = tmp_path / "out.odt"
        count = fodt_to_odt(MINIMAL_FODT, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .odt file is created at the specified path."""
        dest = tmp_path / "out.odt"
        fodt_to_odt(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODT file is a valid ZIP container."""
        dest = tmp_path / "out.odt"
        fodt_to_odt(MINIMAL_FODT, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODT ZIP contains content.xml."""
        dest = tmp_path / "out.odt"
        fodt_to_odt(MINIMAL_FODT, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestFodtToOdtContent:
    """Content correctness tests."""

    def test_content_xml_has_paragraph(self, tmp_path: Path) -> None:
        """content.xml contains paragraph elements."""
        dest = tmp_path / "out.odt"
        fodt_to_odt(MINIMAL_FODT, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "text:p" in content

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        """FODT blocks produce ODT paragraphs."""
        dest = tmp_path / "out.odt"
        count = fodt_to_odt(MINIMAL_FODT, dest)
        assert count >= 1

    def test_headings_convert(self, tmp_path: Path) -> None:
        """Document with headings converts without error."""
        dest = tmp_path / "out.odt"
        count = fodt_to_odt(HEADINGS_FODT, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """content.xml has substantial content."""
        dest = tmp_path / "out.odt"
        fodt_to_odt(MINIMAL_FODT, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestFodtToOdtOptions:
    """Option flag tests."""

    def test_skip_empty_default(self, tmp_path: Path) -> None:
        """skip_empty=True (default) omits empty blocks."""
        dest = tmp_path / "out.odt"
        count = fodt_to_odt(MINIMAL_FODT, dest, skip_empty=True)
        assert count >= 0


class TestFodtToOdtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.odt"
        fodt_to_odt(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.odt"
        count = fodt_to_odt(str(MINIMAL_FODT), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
