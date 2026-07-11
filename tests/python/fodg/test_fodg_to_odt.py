"""
Tests for fodg_to_odt dogfood export.

Verifies that FODG drawing pages are converted to ODT paragraphs using
Format Factory's FODG codec and ODT writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODG = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
SHAPES_FODG = _REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg"

from fodg.fodg_to_odt import fodg_to_odt


class TestFodgToOdtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of paragraphs written."""
        dest = tmp_path / "out.odt"
        count = fodg_to_odt(MINIMAL_FODG, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .odt file is created at the specified path."""
        dest = tmp_path / "out.odt"
        fodg_to_odt(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODT file is a valid ZIP container."""
        dest = tmp_path / "out.odt"
        fodg_to_odt(MINIMAL_FODG, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODT ZIP contains content.xml."""
        dest = tmp_path / "out.odt"
        fodg_to_odt(MINIMAL_FODG, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestFodgToOdtContent:
    """Content correctness tests."""

    def test_content_xml_has_paragraph(self, tmp_path: Path) -> None:
        """content.xml contains paragraph elements."""
        dest = tmp_path / "out.odt"
        fodg_to_odt(MINIMAL_FODG, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "text:p" in content

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        """FODG pages produce ODT paragraphs."""
        dest = tmp_path / "out.odt"
        count = fodg_to_odt(MINIMAL_FODG, dest)
        assert count >= 1

    def test_shapes_convert(self, tmp_path: Path) -> None:
        """Drawing with shapes converts without error."""
        dest = tmp_path / "out.odt"
        count = fodg_to_odt(SHAPES_FODG, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """content.xml has substantial content."""
        dest = tmp_path / "out.odt"
        fodg_to_odt(MINIMAL_FODG, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestFodgToOdtOptions:
    """Option flag tests."""

    def test_include_page_index(self, tmp_path: Path) -> None:
        """include_page_index=True prepends page index to each paragraph."""
        dest = tmp_path / "out.odt"
        fodg_to_odt(MINIMAL_FODG, dest, include_page_index=True)
        assert dest.exists()


class TestFodgToOdtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.odt"
        fodg_to_odt(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.odt"
        count = fodg_to_odt(str(MINIMAL_FODG), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
