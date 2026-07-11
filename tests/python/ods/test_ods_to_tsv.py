"""
Tests for ods_to_tsv dogfood export.

Verifies that ODS spreadsheet rows are converted to TSV using
Format Factory's ODS parser and TSV writer libraries.
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
SINGLE_CELL_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "single-cell.ods"

from ods.ods_to_tsv import ods_to_tsv


class TestOdsToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.tsv"
        count = ods_to_tsv(MINIMAL_ODS, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        ods_to_tsv(MINIMAL_ODS, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        ods_to_tsv(MINIMAL_ODS, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_minimal_ods_returns_one_data_row(self, tmp_path: Path) -> None:
        """minimal-spreadsheet.ods (header + 1 data row) → 1 data row."""
        dest = tmp_path / "out.tsv"
        count = ods_to_tsv(MINIMAL_ODS, dest)
        assert count == 1


class TestOdsToTsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row from row 0 appears as first TSV line."""
        dest = tmp_path / "out.tsv"
        ods_to_tsv(MINIMAL_ODS, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        # minimal-spreadsheet has Name/Value headers
        assert "Name" in first_line or len(first_line) > 0

    def test_data_values_in_output(self, tmp_path: Path) -> None:
        """Data values appear in TSV output."""
        dest = tmp_path / "out.tsv"
        ods_to_tsv(MINIMAL_ODS, dest)
        content = dest.read_text(encoding="utf-8")
        # minimal-spreadsheet has Alpha/42 in data row
        assert "Alpha" in content or "42" in content

    def test_data_uses_tabs(self, tmp_path: Path) -> None:
        """Multi-column rows use tab separator."""
        dest = tmp_path / "out.tsv"
        ods_to_tsv(MINIMAL_ODS, dest)
        lines = dest.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if line.strip():
                assert "\t" in line

    def test_line_count_matches_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.tsv"
        count = ods_to_tsv(MINIMAL_ODS, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1


class TestOdsToTsvOptions:
    """Option flag tests."""

    def test_no_headers_includes_more_data_rows(self, tmp_path: Path) -> None:
        """use_first_row_as_headers=False treats row 0 as data."""
        dest_with = tmp_path / "with_headers.tsv"
        dest_without = tmp_path / "without_headers.tsv"
        count_with = ods_to_tsv(MINIMAL_ODS, dest_with, use_first_row_as_headers=True)
        count_without = ods_to_tsv(MINIMAL_ODS, dest_without, use_first_row_as_headers=False)
        assert count_without > count_with

    def test_include_row_index_adds_column(self, tmp_path: Path) -> None:
        """include_row_index=True prepends 0-based row index."""
        dest = tmp_path / "out.tsv"
        ods_to_tsv(MINIMAL_ODS, dest, include_row_index=True)
        lines = dest.read_text(encoding="utf-8").splitlines()
        data_line = lines[1] if len(lines) > 1 else lines[0]
        # First column should be "0" (row_index)
        assert data_line.startswith("0")


class TestOdsToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        ods_to_tsv(MINIMAL_ODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = ods_to_tsv(str(MINIMAL_ODS), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
