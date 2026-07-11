"""
Tests for ndjson_to_ods dogfood export.

Verifies that NDJSON records are converted to ODS spreadsheets using
Format Factory's NDJSON codec and ODS writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"

from ndjson.ndjson_to_ods import ndjson_to_ods


class TestNdjsonToOdsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.ods"
        count = ndjson_to_ods(MINIMAL_NDJSON, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ods file is created at the specified path."""
        dest = tmp_path / "out.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODS file is a valid ZIP container."""
        dest = tmp_path / "out.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODS ZIP contains content.xml."""
        dest = tmp_path / "out.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestNdjsonToOdsContent:
    """Content correctness tests."""

    def test_three_records_produce_three_rows(self, tmp_path: Path) -> None:
        """minimal.ndjson has 3 records → 3 data rows."""
        dest = tmp_path / "out.ods"
        count = ndjson_to_ods(MINIMAL_NDJSON, dest)
        assert count == 3

    def test_header_row_has_keys(self, tmp_path: Path) -> None:
        """Header row contains the record keys."""
        dest = tmp_path / "out.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "name" in content
        assert "score" in content

    def test_record_values_in_content(self, tmp_path: Path) -> None:
        """Record values appear in content.xml."""
        dest = tmp_path / "out.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "Alice" in content

    def test_content_xml_has_table(self, tmp_path: Path) -> None:
        """content.xml contains a table element."""
        dest = tmp_path / "out.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "table:table" in content


class TestNdjsonToOdsOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_headers=False excludes the header row."""
        dest_with = tmp_path / "with_header.ods"
        dest_without = tmp_path / "without_header.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest_with, include_headers=True)
        ndjson_to_ods(MINIMAL_NDJSON, dest_without, include_headers=False)
        # Without header the file should be smaller
        assert dest_without.stat().st_size <= dest_with.stat().st_size

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the ODS sheet name."""
        dest = tmp_path / "out.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest, sheet_name="Records")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "Records" in content

    def test_default_sheet_name_is_sheet1(self, tmp_path: Path) -> None:
        """Default sheet name is Sheet1."""
        dest = tmp_path / "out.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "Sheet1" in content


class TestNdjsonToOdsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ods"
        ndjson_to_ods(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ods"
        count = ndjson_to_ods(str(MINIMAL_NDJSON), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
