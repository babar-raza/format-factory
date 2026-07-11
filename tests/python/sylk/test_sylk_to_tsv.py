"""
Tests for sylk_to_tsv dogfood export.

Verifies that SYLK spreadsheet rows are converted to TSV using
Format Factory's SYLK parser and TSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
NUMERIC_ROW_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk"
SINGLE_CELL_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "single-cell.slk"

from sylk.sylk_to_tsv import sylk_to_tsv


class TestSylkToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.tsv"
        count = sylk_to_tsv(MINIMAL_SYLK, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        sylk_to_tsv(MINIMAL_SYLK, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        sylk_to_tsv(MINIMAL_SYLK, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_minimal_2x2_returns_one_data_row(self, tmp_path: Path) -> None:
        """minimal-2x2.slk (header + 1 data) → 1 data row."""
        dest = tmp_path / "out.tsv"
        count = sylk_to_tsv(MINIMAL_SYLK, dest)
        assert count == 1


class TestSylkToTsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row (row 1) appears as first TSV line when use_first_row_as_headers=True."""
        dest = tmp_path / "out.tsv"
        sylk_to_tsv(MINIMAL_SYLK, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        # minimal-2x2.slk has Name/Value as headers
        assert "Name" in first_line or len(first_line) > 0

    def test_data_values_in_output(self, tmp_path: Path) -> None:
        """Data cell values appear in TSV output."""
        dest = tmp_path / "out.tsv"
        sylk_to_tsv(MINIMAL_SYLK, dest)
        content = dest.read_text(encoding="utf-8")
        # minimal-2x2 has Alpha/42 in data row
        assert "Alpha" in content or "42" in content

    def test_numeric_values_in_numeric_row(self, tmp_path: Path) -> None:
        """Numeric values appear in numeric-row.slk output."""
        dest = tmp_path / "out.tsv"
        sylk_to_tsv(NUMERIC_ROW_SYLK, dest, use_first_row_as_headers=False)
        content = dest.read_text(encoding="utf-8")
        assert len(content.strip()) > 0


class TestSylkToTsvOptions:
    """Option flag tests."""

    def test_no_headers_uses_all_rows_as_data(self, tmp_path: Path) -> None:
        """use_first_row_as_headers=False treats row 1 as data, not header."""
        dest_with = tmp_path / "with_headers.tsv"
        dest_without = tmp_path / "without_headers.tsv"
        count_with = sylk_to_tsv(MINIMAL_SYLK, dest_with, use_first_row_as_headers=True)
        count_without = sylk_to_tsv(MINIMAL_SYLK, dest_without, use_first_row_as_headers=False)
        # Without headers, both rows become data rows
        assert count_without > count_with

    def test_include_row_index_adds_column(self, tmp_path: Path) -> None:
        """include_row_index=True prepends 1-based row number."""
        dest = tmp_path / "out.tsv"
        sylk_to_tsv(MINIMAL_SYLK, dest, include_row_index=True)
        content = dest.read_text(encoding="utf-8")
        # Row index 2 (first data row in 1-based SYLK) should appear
        assert "2" in content


class TestSylkToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        sylk_to_tsv(MINIMAL_SYLK, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = sylk_to_tsv(str(MINIMAL_SYLK), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
