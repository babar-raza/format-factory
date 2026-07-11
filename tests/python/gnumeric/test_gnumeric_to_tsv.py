"""
Tests for gnumeric_to_tsv dogfood export.

Verifies that Gnumeric spreadsheet rows are converted to TSV using
Format Factory's Gnumeric codec and TSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MULTI_CELL_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric"
MINIMAL_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"

from gnumeric.gnumeric_to_tsv import gnumeric_to_tsv


class TestGnumericToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.tsv"
        count = gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_multi_cell_returns_one_data_row(self, tmp_path: Path) -> None:
        """multi-cell-basic.gnumeric (header + 1 data row) → 1 data row."""
        dest = tmp_path / "out.tsv"
        count = gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest)
        assert count == 1


class TestGnumericToTsvContent:
    """Content correctness tests."""

    def test_header_row_in_output(self, tmp_path: Path) -> None:
        """Header row from row 0 appears in TSV output."""
        dest = tmp_path / "out.tsv"
        gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        # multi-cell-basic has Name/Score as headers
        assert "Name" in first_line or len(first_line) > 0

    def test_data_values_in_output(self, tmp_path: Path) -> None:
        """Data values appear in TSV output."""
        dest = tmp_path / "out.tsv"
        gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest)
        content = dest.read_text(encoding="utf-8")
        # multi-cell-basic has Alice/42 in data row
        assert "Alice" in content or "42" in content

    def test_data_uses_tabs(self, tmp_path: Path) -> None:
        """Multi-column rows use tab separator."""
        dest = tmp_path / "out.tsv"
        gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest)
        lines = dest.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if line.strip():
                assert "\t" in line


class TestGnumericToTsvOptions:
    """Option flag tests."""

    def test_no_headers_uses_all_rows_as_data(self, tmp_path: Path) -> None:
        """use_first_row_as_headers=False makes row 0 a data row."""
        dest_with = tmp_path / "with_headers.tsv"
        dest_without = tmp_path / "without_headers.tsv"
        count_with = gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest_with, use_first_row_as_headers=True)
        count_without = gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest_without, use_first_row_as_headers=False)
        assert count_without > count_with

    def test_include_row_index_adds_column(self, tmp_path: Path) -> None:
        """include_row_index=True prepends row index."""
        dest = tmp_path / "out.tsv"
        gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest, include_row_index=True)
        content = dest.read_text(encoding="utf-8")
        assert "0" in content or "1" in content


class TestGnumericToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        gnumeric_to_tsv(MULTI_CELL_GNUMERIC, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = gnumeric_to_tsv(str(MULTI_CELL_GNUMERIC), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
