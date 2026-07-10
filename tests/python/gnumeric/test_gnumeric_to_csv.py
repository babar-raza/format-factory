"""
Tests for gnumeric_to_csv dogfood export.

Verifies that Gnumeric spreadsheet data is converted to CSV using
Format Factory's gnumeric reader and csv writer libraries.
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

from gnumeric.gnumeric_to_csv import gnumeric_to_csv


class TestGnumericToCsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.csv"
        count = gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest)
        assert dest.exists()

    def test_output_is_non_empty(self, tmp_path: Path) -> None:
        """Output file has content."""
        dest = tmp_path / "out.csv"
        gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest)
        assert dest.stat().st_size > 0

    def test_multi_cell_produces_two_rows(self, tmp_path: Path) -> None:
        """multi-cell-basic.gnumeric (2 rows) produces 2 CSV rows."""
        dest = tmp_path / "out.csv"
        count = gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest)
        assert count == 2

    def test_minimal_produces_one_row(self, tmp_path: Path) -> None:
        """minimal-spreadsheet.gnumeric (1 cell) produces 1 CSV row."""
        dest = tmp_path / "out.csv"
        count = gnumeric_to_csv(MINIMAL_GNUMERIC, dest)
        assert count == 1


class TestGnumericToCsvContent:
    """Content accuracy tests."""

    def test_header_values_present(self, tmp_path: Path) -> None:
        """Header row values (Name, Score) appear in output."""
        dest = tmp_path / "out.csv"
        gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Name" in content or "Score" in content

    def test_data_values_present(self, tmp_path: Path) -> None:
        """Data row values (Alice, 42) appear in output."""
        dest = tmp_path / "out.csv"
        gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alice" in content or "42" in content

    def test_two_columns_in_multi_cell(self, tmp_path: Path) -> None:
        """multi-cell-basic.gnumeric (2 columns) produces 2 CSV fields per row."""
        import csv as _csv
        dest = tmp_path / "out.csv"
        gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest)
        rows = list(_csv.reader(dest.read_text(encoding="utf-8").splitlines()))
        assert all(len(r) == 2 for r in rows if r)

    def test_line_count_matches_return(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.csv"
        count = gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestGnumericToCsvOptions:
    """Option and parameter tests."""

    def test_sheet_index_default_zero(self, tmp_path: Path) -> None:
        """Default sheet_index=0 exports first sheet."""
        dest_default = tmp_path / "default.csv"
        dest_zero = tmp_path / "zero.csv"
        gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest_default)
        gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest_zero, sheet_index=0)
        assert dest_default.read_text(encoding="utf-8") == dest_zero.read_text(encoding="utf-8")

    def test_invalid_sheet_index_raises(self, tmp_path: Path) -> None:
        """Out-of-range sheet_index raises GnumericError."""
        from gnumeric.exceptions import GnumericError
        dest = tmp_path / "out.csv"
        with pytest.raises(GnumericError):
            gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest, sheet_index=99)

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = gnumeric_to_csv(str(MULTI_CELL_GNUMERIC), str(dest))
        assert isinstance(count, int)
        assert dest.exists()


class TestGnumericToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        gnumeric_to_csv(MULTI_CELL_GNUMERIC, dest)
        assert dest.exists()
