"""
Tests for abw_to_ods dogfood export.

Verifies that ABW paragraphs are converted to ODS rows using
Format Factory's ABW codec and ODS writer libraries.
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

from abw.abw_to_ods import abw_to_ods


class TestAbwToOdsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.ods"
        count = abw_to_ods(MINIMAL_ABW, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ods file is created at the specified path."""
        dest = tmp_path / "out.ods"
        abw_to_ods(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODS file is a valid ZIP container."""
        dest = tmp_path / "out.ods"
        abw_to_ods(MINIMAL_ABW, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODS ZIP contains content.xml."""
        dest = tmp_path / "out.ods"
        abw_to_ods(MINIMAL_ABW, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestAbwToOdsContent:
    """Content correctness tests."""

    def test_content_xml_has_table(self, tmp_path: Path) -> None:
        """content.xml contains a table element."""
        dest = tmp_path / "out.ods"
        abw_to_ods(MINIMAL_ABW, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "table:table" in content

    def test_header_row_with_text_column(self, tmp_path: Path) -> None:
        """Header row with 'text' column name is present by default."""
        dest = tmp_path / "out.ods"
        abw_to_ods(MINIMAL_ABW, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "text" in content

    def test_two_paragraphs_produce_two_rows(self, tmp_path: Path) -> None:
        """two-paragraphs.abw produces at least 2 data rows."""
        dest = tmp_path / "out.ods"
        count = abw_to_ods(TWO_PARA_ABW, dest)
        assert count >= 2

    def test_paragraph_text_in_content(self, tmp_path: Path) -> None:
        """ABW paragraph text appears in content.xml."""
        dest = tmp_path / "out.ods"
        abw_to_ods(TWO_PARA_ABW, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestAbwToOdsOptions:
    """Option flag tests."""

    def test_no_header(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.ods"
        abw_to_ods(MINIMAL_ABW, dest, include_header=False)
        assert dest.exists()

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the ODS sheet name."""
        dest = tmp_path / "out.ods"
        abw_to_ods(MINIMAL_ABW, dest, sheet_name="Paragraphs")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "Paragraphs" in content

    def test_skip_empty_by_default(self, tmp_path: Path) -> None:
        """skip_empty=True by default omits empty paragraphs."""
        dest = tmp_path / "out.ods"
        count = abw_to_ods(MINIMAL_ABW, dest, skip_empty=True)
        assert count >= 0


class TestAbwToOdsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ods"
        abw_to_ods(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ods"
        count = abw_to_ods(str(MINIMAL_ABW), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
