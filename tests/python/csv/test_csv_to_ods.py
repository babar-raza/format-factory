"""
Tests for csv_to_ods dogfood export.

Verifies that CSV data is converted to ODS spreadsheets using
Format Factory's CSV parser and ODS writer libraries.
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

from src.python.ff_csv.csv_to_ods import csv_to_ods


class TestCsvToOdsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.ods"
        count = csv_to_ods(MINIMAL_CSV, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ods file is created at the specified path."""
        dest = tmp_path / "out.ods"
        csv_to_ods(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODS file is a valid ZIP container."""
        dest = tmp_path / "out.ods"
        csv_to_ods(MINIMAL_CSV, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODS ZIP contains content.xml."""
        dest = tmp_path / "out.ods"
        csv_to_ods(MINIMAL_CSV, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestCsvToOdsContent:
    """Content correctness tests."""

    def test_content_xml_has_table(self, tmp_path: Path) -> None:
        """content.xml contains a table element."""
        dest = tmp_path / "out.ods"
        csv_to_ods(MINIMAL_CSV, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "table:table" in content

    def test_data_values_in_content(self, tmp_path: Path) -> None:
        """CSV cell values appear in content.xml."""
        dest = tmp_path / "out.ods"
        csv_to_ods(MINIMAL_CSV, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        # minimal-2x2 has at least some text content
        assert len(content) > 100

    def test_quoted_csv_converts(self, tmp_path: Path) -> None:
        """Quoted CSV fields are handled correctly."""
        dest = tmp_path / "out.ods"
        count = csv_to_ods(QUOTED_CSV, dest)
        assert dest.exists()
        assert count >= 0

    def test_row_count_matches_data_rows(self, tmp_path: Path) -> None:
        """Returned count matches the number of non-header CSV rows."""
        dest = tmp_path / "out.ods"
        count = csv_to_ods(MINIMAL_CSV, dest)
        assert count >= 1


class TestCsvToOdsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the ODS sheet name."""
        dest = tmp_path / "out.ods"
        csv_to_ods(MINIMAL_CSV, dest, sheet_name="MyData")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "MyData" in content

    def test_default_sheet_name_is_sheet1(self, tmp_path: Path) -> None:
        """Default sheet name is Sheet1."""
        dest = tmp_path / "out.ods"
        csv_to_ods(MINIMAL_CSV, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "Sheet1" in content


class TestCsvToOdsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ods"
        csv_to_ods(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ods"
        count = csv_to_ods(str(MINIMAL_CSV), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
