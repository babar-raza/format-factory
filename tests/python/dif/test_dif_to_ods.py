"""
Tests for dif_to_ods dogfood export.

Verifies that DIF rows are converted to ODS rows using
Format Factory's DIF parser and ODS writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
NUMERIC_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "numeric-row.dif"

from dif.dif_to_ods import dif_to_ods


class TestDifToOdsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.ods"
        count = dif_to_ods(MINIMAL_DIF, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ods file is created at the specified path."""
        dest = tmp_path / "out.ods"
        dif_to_ods(MINIMAL_DIF, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODS file is a valid ZIP container."""
        dest = tmp_path / "out.ods"
        dif_to_ods(MINIMAL_DIF, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODS ZIP contains content.xml."""
        dest = tmp_path / "out.ods"
        dif_to_ods(MINIMAL_DIF, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestDifToOdsContent:
    """Content correctness tests."""

    def test_content_xml_has_table(self, tmp_path: Path) -> None:
        """content.xml contains a table element."""
        dest = tmp_path / "out.ods"
        dif_to_ods(MINIMAL_DIF, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "table:table" in content

    def test_produces_rows(self, tmp_path: Path) -> None:
        """DIF document produces ODS rows."""
        dest = tmp_path / "out.ods"
        count = dif_to_ods(MINIMAL_DIF, dest)
        assert count >= 1

    def test_numeric_row_converts(self, tmp_path: Path) -> None:
        """Numeric DIF row converts without error."""
        dest = tmp_path / "out.ods"
        count = dif_to_ods(NUMERIC_DIF, dest)
        assert dest.exists()
        assert count >= 1


class TestDifToOdsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the ODS sheet name."""
        dest = tmp_path / "out.ods"
        dif_to_ods(MINIMAL_DIF, dest, sheet_name="DIF_Data")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "DIF_Data" in content

    def test_include_row_index(self, tmp_path: Path) -> None:
        """include_row_index=True prepends a row index column."""
        dest_plain = tmp_path / "out_plain.ods"
        dest_idx = tmp_path / "out_idx.ods"
        count_plain = dif_to_ods(MINIMAL_DIF, dest_plain)
        count_idx = dif_to_ods(MINIMAL_DIF, dest_idx, include_row_index=True)
        assert count_idx == count_plain


class TestDifToOdsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ods"
        dif_to_ods(MINIMAL_DIF, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ods"
        count = dif_to_ods(str(MINIMAL_DIF), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
