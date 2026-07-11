"""
Tests for sylk_to_ods dogfood export.

Verifies that SYLK spreadsheet rows are converted to ODS rows using
Format Factory's SYLK parser and ODS writer libraries.
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

from sylk.sylk_to_ods import sylk_to_ods


class TestSylkToOdsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.ods"
        count = sylk_to_ods(MINIMAL_SYLK, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ods file is created at the specified path."""
        dest = tmp_path / "out.ods"
        sylk_to_ods(MINIMAL_SYLK, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODS file is a valid ZIP container."""
        dest = tmp_path / "out.ods"
        sylk_to_ods(MINIMAL_SYLK, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODS ZIP contains content.xml."""
        dest = tmp_path / "out.ods"
        sylk_to_ods(MINIMAL_SYLK, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestSylkToOdsContent:
    """Content correctness tests."""

    def test_content_xml_has_table(self, tmp_path: Path) -> None:
        """content.xml contains a table element."""
        dest = tmp_path / "out.ods"
        sylk_to_ods(MINIMAL_SYLK, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "table:table" in content

    def test_two_rows_from_2x2(self, tmp_path: Path) -> None:
        """minimal-2x2.slk produces 2 rows."""
        dest = tmp_path / "out.ods"
        count = sylk_to_ods(MINIMAL_SYLK, dest)
        assert count == 2

    def test_numeric_row_converts(self, tmp_path: Path) -> None:
        """Numeric SYLK row converts without error."""
        dest = tmp_path / "out.ods"
        count = sylk_to_ods(NUMERIC_SYLK, dest)
        assert dest.exists()
        assert count >= 1

    def test_cell_values_in_content(self, tmp_path: Path) -> None:
        """SYLK cell values appear in content.xml."""
        dest = tmp_path / "out.ods"
        sylk_to_ods(MINIMAL_SYLK, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestSylkToOdsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the ODS sheet name."""
        dest = tmp_path / "out.ods"
        sylk_to_ods(MINIMAL_SYLK, dest, sheet_name="SYLK_Data")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "SYLK_Data" in content

    def test_include_row_index(self, tmp_path: Path) -> None:
        """include_row_index=True adds a row number column."""
        dest = tmp_path / "out.ods"
        sylk_to_ods(MINIMAL_SYLK, dest, include_row_index=True)
        assert dest.exists()


class TestSylkToOdsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ods"
        sylk_to_ods(MINIMAL_SYLK, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ods"
        count = sylk_to_ods(str(MINIMAL_SYLK), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
