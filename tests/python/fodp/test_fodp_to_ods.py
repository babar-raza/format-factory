"""
Tests for fodp_to_ods dogfood export.

Verifies that FODP presentation slides are converted to ODS rows using
Format Factory's FODP codec and ODS writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
TWO_SLIDES = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"

from fodp.fodp_to_ods import fodp_to_ods


class TestFodpToOdsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of slides written."""
        dest = tmp_path / "out.ods"
        count = fodp_to_ods(MINIMAL_FODP, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ods file is created at the specified path."""
        dest = tmp_path / "out.ods"
        fodp_to_ods(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODS file is a valid ZIP container."""
        dest = tmp_path / "out.ods"
        fodp_to_ods(MINIMAL_FODP, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODS ZIP contains content.xml."""
        dest = tmp_path / "out.ods"
        fodp_to_ods(MINIMAL_FODP, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestFodpToOdsContent:
    """Content correctness tests."""

    def test_content_xml_has_table(self, tmp_path: Path) -> None:
        """content.xml contains a table element."""
        dest = tmp_path / "out.ods"
        fodp_to_ods(MINIMAL_FODP, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "table:table" in content

    def test_produces_rows(self, tmp_path: Path) -> None:
        """FODP slides produce ODS rows."""
        dest = tmp_path / "out.ods"
        count = fodp_to_ods(MINIMAL_FODP, dest)
        assert count >= 1

    def test_two_slides_convert(self, tmp_path: Path) -> None:
        """Two-slide FODP converts without error."""
        dest = tmp_path / "out.ods"
        count = fodp_to_ods(TWO_SLIDES, dest)
        assert dest.exists()
        assert count >= 2

    def test_content_has_data(self, tmp_path: Path) -> None:
        """content.xml has substantial content."""
        dest = tmp_path / "out.ods"
        fodp_to_ods(MINIMAL_FODP, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestFodpToOdsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the ODS sheet name."""
        dest = tmp_path / "out.ods"
        fodp_to_ods(MINIMAL_FODP, dest, sheet_name="FODP_Data")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "FODP_Data" in content

    def test_include_header(self, tmp_path: Path) -> None:
        """include_header=True writes a header row."""
        dest = tmp_path / "out.ods"
        fodp_to_ods(MINIMAL_FODP, dest, include_header=True)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "slide_name" in content

    def test_include_slide_index(self, tmp_path: Path) -> None:
        """include_slide_index=True adds a slide_index column."""
        dest = tmp_path / "out.ods"
        fodp_to_ods(MINIMAL_FODP, dest, include_slide_index=True)
        assert dest.exists()


class TestFodpToOdsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ods"
        fodp_to_ods(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ods"
        count = fodp_to_ods(str(MINIMAL_FODP), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
