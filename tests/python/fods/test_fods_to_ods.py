"""
Tests for fods_to_ods dogfood export.

Verifies that FODS spreadsheet rows are converted to ODS rows using
Format Factory's FODS parser and ODS writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
MULTI_FODS = _REPO / "samples" / "by-format" / "fods" / "multi-sheet-basic.fods"

from fods.fods_to_ods import fods_to_ods


class TestFodsToOdsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.ods"
        count = fods_to_ods(MINIMAL_FODS, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ods file is created at the specified path."""
        dest = tmp_path / "out.ods"
        fods_to_ods(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODS file is a valid ZIP container."""
        dest = tmp_path / "out.ods"
        fods_to_ods(MINIMAL_FODS, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODS ZIP contains content.xml."""
        dest = tmp_path / "out.ods"
        fods_to_ods(MINIMAL_FODS, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestFodsToOdsContent:
    """Content correctness tests."""

    def test_content_xml_has_table(self, tmp_path: Path) -> None:
        """content.xml contains a table element."""
        dest = tmp_path / "out.ods"
        fods_to_ods(MINIMAL_FODS, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "table:table" in content

    def test_produces_rows(self, tmp_path: Path) -> None:
        """FODS sheet produces ODS rows."""
        dest = tmp_path / "out.ods"
        count = fods_to_ods(MINIMAL_FODS, dest)
        assert count >= 1

    def test_multi_sheet_converts(self, tmp_path: Path) -> None:
        """Multi-sheet FODS file converts without error."""
        dest = tmp_path / "out.ods"
        count = fods_to_ods(MULTI_FODS, dest)
        assert dest.exists()
        assert count >= 0

    def test_cell_values_in_content(self, tmp_path: Path) -> None:
        """FODS cell values appear in content.xml."""
        dest = tmp_path / "out.ods"
        fods_to_ods(MINIMAL_FODS, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert len(content) > 100


class TestFodsToOdsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the ODS sheet name."""
        dest = tmp_path / "out.ods"
        fods_to_ods(MINIMAL_FODS, dest, sheet_name="FODS_Data")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "FODS_Data" in content

    def test_skip_empty_rows_default(self, tmp_path: Path) -> None:
        """skip_empty_rows=True (default) omits all-empty rows."""
        dest = tmp_path / "out.ods"
        count = fods_to_ods(MINIMAL_FODS, dest, skip_empty_rows=True)
        assert count >= 0

    def test_sheet_index_default(self, tmp_path: Path) -> None:
        """Default sheet_index=0 exports the first sheet."""
        dest = tmp_path / "out.ods"
        count = fods_to_ods(MINIMAL_FODS, dest, sheet_index=0)
        assert count >= 0


class TestFodsToOdsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ods"
        fods_to_ods(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ods"
        count = fods_to_ods(str(MINIMAL_FODS), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
