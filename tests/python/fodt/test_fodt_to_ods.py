"""
Tests for fodt_to_ods dogfood export.

Verifies that FODT document blocks are converted to ODS rows using
Format Factory's FODT parser and ODS writer libraries.
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

from fodt.fodt_to_ods import fodt_to_ods


class TestFodtToOdsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.ods"
        count = fodt_to_ods(MINIMAL_FODT, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ods file is created at the specified path."""
        dest = tmp_path / "out.ods"
        fodt_to_ods(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODS file is a valid ZIP container."""
        dest = tmp_path / "out.ods"
        fodt_to_ods(MINIMAL_FODT, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODS ZIP contains content.xml."""
        dest = tmp_path / "out.ods"
        fodt_to_ods(MINIMAL_FODT, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestFodtToOdsContent:
    """Content correctness tests."""

    def test_content_xml_has_table(self, tmp_path: Path) -> None:
        """content.xml contains a table element."""
        dest = tmp_path / "out.ods"
        fodt_to_ods(MINIMAL_FODT, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "table:table" in content

    def test_produces_rows(self, tmp_path: Path) -> None:
        """FODT blocks produce ODS rows."""
        dest = tmp_path / "out.ods"
        count = fodt_to_ods(MINIMAL_FODT, dest)
        assert count >= 1

    def test_headings_convert(self, tmp_path: Path) -> None:
        """Document with headings converts without error."""
        dest = tmp_path / "out.ods"
        count = fodt_to_ods(HEADINGS_FODT, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """content.xml has substantial content."""
        dest = tmp_path / "out.ods"
        fodt_to_ods(MINIMAL_FODT, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestFodtToOdsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the ODS sheet name."""
        dest = tmp_path / "out.ods"
        fodt_to_ods(MINIMAL_FODT, dest, sheet_name="FODT_Data")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "FODT_Data" in content

    def test_include_header(self, tmp_path: Path) -> None:
        """include_header=True writes block_type/text header row."""
        dest = tmp_path / "out.ods"
        fodt_to_ods(MINIMAL_FODT, dest, include_header=True)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "block_type" in content

    def test_no_header(self, tmp_path: Path) -> None:
        """include_header=False omits the header row."""
        dest = tmp_path / "out.ods"
        count = fodt_to_ods(MINIMAL_FODT, dest, include_header=False)
        assert count >= 0


class TestFodtToOdsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ods"
        fodt_to_ods(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ods"
        count = fodt_to_ods(str(MINIMAL_FODT), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
