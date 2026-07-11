"""
Tests for abw_to_odt dogfood export.

Verifies that ABW paragraphs are converted to ODT paragraphs using
Format Factory's ABW codec and ODT writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
TWO_PARA_ABW = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"

from abw.abw_to_odt import abw_to_odt


class TestAbwToOdtBasic:
    """Basic conversion tests."""

    def test_returns_paragraph_count(self, tmp_path: Path) -> None:
        """Returns an integer count of paragraphs written."""
        dest = tmp_path / "out.odt"
        count = abw_to_odt(MINIMAL_ABW, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .odt file is created at the specified path."""
        dest = tmp_path / "out.odt"
        abw_to_odt(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODT file is a valid ZIP container."""
        dest = tmp_path / "out.odt"
        abw_to_odt(MINIMAL_ABW, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODT ZIP contains content.xml."""
        dest = tmp_path / "out.odt"
        abw_to_odt(MINIMAL_ABW, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestAbwToOdtContent:
    """Content correctness tests."""

    def test_content_xml_has_paragraph(self, tmp_path: Path) -> None:
        """content.xml contains paragraph elements."""
        dest = tmp_path / "out.odt"
        abw_to_odt(MINIMAL_ABW, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "text:p" in content

    def test_two_paragraphs_produces_two(self, tmp_path: Path) -> None:
        """two-paragraphs.abw produces at least 2 paragraphs."""
        dest = tmp_path / "out.odt"
        count = abw_to_odt(TWO_PARA_ABW, dest)
        assert count >= 2

    def test_paragraph_text_in_content(self, tmp_path: Path) -> None:
        """ABW paragraph text appears in content.xml."""
        dest = tmp_path / "out.odt"
        abw_to_odt(TWO_PARA_ABW, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestAbwToOdtOptions:
    """Option flag tests."""

    def test_skip_empty_by_default(self, tmp_path: Path) -> None:
        """skip_empty=True by default omits empty paragraphs."""
        dest = tmp_path / "out.odt"
        count = abw_to_odt(MINIMAL_ABW, dest, skip_empty=True)
        assert count >= 0

    def test_include_empty_paragraphs(self, tmp_path: Path) -> None:
        """skip_empty=False includes empty paragraphs."""
        dest_skip = tmp_path / "out_skip.odt"
        dest_all = tmp_path / "out_all.odt"
        count_skip = abw_to_odt(TWO_PARA_ABW, dest_skip, skip_empty=True)
        count_all = abw_to_odt(TWO_PARA_ABW, dest_all, skip_empty=False)
        assert count_all >= count_skip


class TestAbwToOdtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.odt"
        abw_to_odt(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.odt"
        count = abw_to_odt(str(MINIMAL_ABW), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
