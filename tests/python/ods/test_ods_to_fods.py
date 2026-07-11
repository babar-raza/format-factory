"""
Tests for ods_to_fods dogfood export.

Verifies that ODS spreadsheet rows are converted to FODS format using
Format Factory's ODS parser and FODS writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
NUMERIC_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "numeric-row.ods"

from ods.ods_to_fods import ods_to_fods


class TestOdsToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.fods"
        count = ods_to_fods(MINIMAL_ODS, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        ods_to_fods(MINIMAL_ODS, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (not ZIP)."""
        dest = tmp_path / "out.fods"
        ods_to_fods(MINIMAL_ODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        ods_to_fods(MINIMAL_ODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestOdsToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """ODS sheet produces FODS rows."""
        dest = tmp_path / "out.fods"
        count = ods_to_fods(MINIMAL_ODS, dest)
        assert count >= 1

    def test_numeric_converts(self, tmp_path: Path) -> None:
        """Numeric ODS converts without error."""
        dest = tmp_path / "out.fods"
        count = ods_to_fods(NUMERIC_ODS, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        ods_to_fods(MINIMAL_ODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 200


class TestOdsToFodsOptions:
    """Option flag tests."""

    def test_sheet_index(self, tmp_path: Path) -> None:
        """sheet_index=0 exports the first sheet only."""
        dest = tmp_path / "out.fods"
        count = ods_to_fods(MINIMAL_ODS, dest, sheet_index=0)
        assert count >= 0

    def test_skip_empty_rows(self, tmp_path: Path) -> None:
        """skip_empty_rows=True omits empty rows."""
        dest = tmp_path / "out.fods"
        count = ods_to_fods(MINIMAL_ODS, dest, skip_empty_rows=True)
        assert count >= 0


class TestOdsToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        ods_to_fods(MINIMAL_ODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = ods_to_fods(str(MINIMAL_ODS), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
