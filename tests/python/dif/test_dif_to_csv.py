"""
Tests for dif_to_csv dogfood export.

Verifies that DIF spreadsheet rows are converted to CSV using
Format Factory's dif reader and csv writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

NUMERIC_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "numeric-row.dif"
SINGLE_CELL_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "single-cell.dif"

from src.python.dif.dif_to_csv import dif_to_csv


class TestDifToCsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.csv"
        count = dif_to_csv(NUMERIC_DIF, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        dif_to_csv(NUMERIC_DIF, dest)
        assert dest.exists()

    def test_output_is_non_empty(self, tmp_path: Path) -> None:
        """Output file has content."""
        dest = tmp_path / "out.csv"
        dif_to_csv(NUMERIC_DIF, dest)
        assert dest.stat().st_size > 0

    def test_numeric_row_produces_one_row(self, tmp_path: Path) -> None:
        """numeric-row.dif (1 tuple) produces 1 CSV row."""
        dest = tmp_path / "out.csv"
        count = dif_to_csv(NUMERIC_DIF, dest)
        assert count == 1

    def test_single_cell_produces_one_row(self, tmp_path: Path) -> None:
        """single-cell.dif (1 tuple, 1 vector) produces 1 CSV row."""
        dest = tmp_path / "out.csv"
        count = dif_to_csv(SINGLE_CELL_DIF, dest)
        assert count == 1


class TestDifToCsvContent:
    """Content accuracy tests."""

    def test_numeric_values_in_output(self, tmp_path: Path) -> None:
        """Numeric cell values appear in CSV output."""
        dest = tmp_path / "out.csv"
        dif_to_csv(NUMERIC_DIF, dest)
        content = dest.read_text(encoding="utf-8")
        # numeric-row.dif has values 1, 2, 3
        assert "1" in content and "2" in content

    def test_single_cell_value_in_output(self, tmp_path: Path) -> None:
        """Single cell value (42) appears in CSV output."""
        dest = tmp_path / "out.csv"
        dif_to_csv(SINGLE_CELL_DIF, dest)
        content = dest.read_text(encoding="utf-8")
        assert "42" in content

    def test_line_count_matches_return(self, tmp_path: Path) -> None:
        """Non-empty line count in output matches the return value."""
        dest = tmp_path / "out.csv"
        count = dif_to_csv(NUMERIC_DIF, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_three_columns_in_numeric_row(self, tmp_path: Path) -> None:
        """numeric-row.dif has 3 vectors, producing 3 CSV fields."""
        import csv as _csv
        dest = tmp_path / "out.csv"
        dif_to_csv(NUMERIC_DIF, dest)
        rows = list(_csv.reader(dest.read_text(encoding="utf-8").splitlines()))
        assert len(rows) >= 1
        assert len(rows[0]) == 3


class TestDifToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        dif_to_csv(NUMERIC_DIF, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = dif_to_csv(str(NUMERIC_DIF), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
