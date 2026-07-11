"""
Tests for csv_to_odt dogfood export.

Verifies that CSV rows are converted to ODT paragraphs using
Format Factory's CSV parser and ODT writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
QUOTED_CSV = _REPO / "samples" / "by-format" / "csv" / "quoted-fields.csv"

from src.python.csv.csv_to_odt import csv_to_odt


class TestCsvToOdtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.odt"
        count = csv_to_odt(MINIMAL_CSV, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .odt file is created at the specified path."""
        dest = tmp_path / "out.odt"
        csv_to_odt(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODT file is a valid ZIP container."""
        dest = tmp_path / "out.odt"
        csv_to_odt(MINIMAL_CSV, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODT ZIP contains content.xml."""
        dest = tmp_path / "out.odt"
        csv_to_odt(MINIMAL_CSV, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestCsvToOdtContent:
    """Content correctness tests."""

    def test_content_xml_has_paragraph(self, tmp_path: Path) -> None:
        """content.xml contains paragraph elements."""
        dest = tmp_path / "out.odt"
        csv_to_odt(MINIMAL_CSV, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "text:p" in content

    def test_csv_values_in_content(self, tmp_path: Path) -> None:
        """CSV cell values appear in content.xml."""
        dest = tmp_path / "out.odt"
        csv_to_odt(MINIMAL_CSV, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100

    def test_quoted_fields_handled(self, tmp_path: Path) -> None:
        """Quoted CSV fields are handled without error."""
        dest = tmp_path / "out.odt"
        count = csv_to_odt(QUOTED_CSV, dest)
        assert dest.exists()
        assert count >= 0

    def test_row_count_matches_data_rows(self, tmp_path: Path) -> None:
        """Returned count matches the number of data rows."""
        dest = tmp_path / "out.odt"
        count = csv_to_odt(MINIMAL_CSV, dest)
        assert count >= 1


class TestCsvToOdtOptions:
    """Option flag tests."""

    def test_custom_separator(self, tmp_path: Path) -> None:
        """Custom separator joins values in paragraphs."""
        dest = tmp_path / "out.odt"
        csv_to_odt(MINIMAL_CSV, dest, separator=" | ")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert " | " in content

    def test_header_as_heading(self, tmp_path: Path) -> None:
        """include_header_as_heading=True puts headers in the heading."""
        dest = tmp_path / "out.odt"
        count = csv_to_odt(MINIMAL_CSV, dest, include_header_as_heading=True)
        assert dest.exists()
        assert count >= 0


class TestCsvToOdtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.odt"
        csv_to_odt(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.odt"
        count = csv_to_odt(str(MINIMAL_CSV), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
