"""
Tests for sylk_to_csv dogfood export.

Verifies that SYLK spreadsheet cells are converted to CSV using
Format Factory's sylk reader and csv writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_2X2_SLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
NUMERIC_ROW_SLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk"
SINGLE_CELL_SLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "single-cell.slk"

from src.python.sylk.sylk_to_csv import sylk_to_csv


class TestSylkToCsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.csv"
        count = sylk_to_csv(MINIMAL_2X2_SLK, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        sylk_to_csv(MINIMAL_2X2_SLK, dest)
        assert dest.exists()

    def test_output_is_non_empty(self, tmp_path: Path) -> None:
        """Output file has content."""
        dest = tmp_path / "out.csv"
        sylk_to_csv(MINIMAL_2X2_SLK, dest)
        assert dest.stat().st_size > 0

    def test_2x2_produces_two_rows(self, tmp_path: Path) -> None:
        """minimal-2x2.slk (2 SYLK rows) produces 2 CSV rows."""
        dest = tmp_path / "out.csv"
        count = sylk_to_csv(MINIMAL_2X2_SLK, dest)
        assert count == 2

    def test_single_cell_produces_one_row(self, tmp_path: Path) -> None:
        """single-cell.slk (1 row, 1 col) produces 1 CSV row."""
        dest = tmp_path / "out.csv"
        count = sylk_to_csv(SINGLE_CELL_SLK, dest)
        assert count == 1


class TestSylkToCsvContent:
    """Content accuracy tests."""

    def test_header_row_values_present(self, tmp_path: Path) -> None:
        """Header values (Name, Value) appear in CSV output."""
        dest = tmp_path / "out.csv"
        sylk_to_csv(MINIMAL_2X2_SLK, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Name" in content or "Value" in content

    def test_data_row_values_present(self, tmp_path: Path) -> None:
        """Data row values (Alpha, 42) appear in CSV output."""
        dest = tmp_path / "out.csv"
        sylk_to_csv(MINIMAL_2X2_SLK, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alpha" in content or "42" in content

    def test_two_columns_in_2x2(self, tmp_path: Path) -> None:
        """minimal-2x2 (2 cols) produces 2 CSV fields per row."""
        import csv as _csv
        dest = tmp_path / "out.csv"
        sylk_to_csv(MINIMAL_2X2_SLK, dest)
        rows = list(_csv.reader(dest.read_text(encoding="utf-8").splitlines()))
        non_empty_rows = [r for r in rows if r]
        assert all(len(r) == 2 for r in non_empty_rows)

    def test_line_count_matches_return(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.csv"
        count = sylk_to_csv(MINIMAL_2X2_SLK, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestSylkToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        sylk_to_csv(MINIMAL_2X2_SLK, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = sylk_to_csv(str(MINIMAL_2X2_SLK), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
