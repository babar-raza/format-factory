"""
Tests for csv_to_tsv dogfood export.

Verifies that CSV rows are converted to TSV using
Format Factory's CSV parser and TSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
SINGLE_CELL_CSV = _REPO / "samples" / "by-format" / "csv" / "single-cell.csv"
QUOTED_CSV = _REPO / "samples" / "by-format" / "csv" / "quoted-fields.csv"

from src.python.csv.csv_to_tsv import csv_to_tsv


class TestCsvToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.tsv"
        count = csv_to_tsv(MINIMAL_CSV, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        csv_to_tsv(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        csv_to_tsv(MINIMAL_CSV, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_minimal_csv_returns_two_rows(self, tmp_path: Path) -> None:
        """minimal-2x2.csv with 2 data rows → count of 2."""
        dest = tmp_path / "out.tsv"
        count = csv_to_tsv(MINIMAL_CSV, dest)
        assert count == 2


class TestCsvToTsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row from CSV appears as first TSV line."""
        dest = tmp_path / "out.tsv"
        csv_to_tsv(MINIMAL_CSV, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "Name" in first_line

    def test_header_uses_tabs(self, tmp_path: Path) -> None:
        """Header fields are tab-separated (not comma-separated)."""
        dest = tmp_path / "out.tsv"
        csv_to_tsv(MINIMAL_CSV, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "\t" in first_line
        assert "," not in first_line

    def test_data_values_in_output(self, tmp_path: Path) -> None:
        """CSV data values appear in TSV output."""
        dest = tmp_path / "out.tsv"
        csv_to_tsv(MINIMAL_CSV, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alice" in content
        assert "Bob" in content

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.tsv"
        count = csv_to_tsv(MINIMAL_CSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_data_rows_use_tabs(self, tmp_path: Path) -> None:
        """Data rows are tab-delimited."""
        dest = tmp_path / "out.tsv"
        csv_to_tsv(MINIMAL_CSV, dest)
        lines = dest.read_text(encoding="utf-8").splitlines()
        # data rows (not header)
        for line in lines[1:]:
            if line.strip():
                assert "\t" in line


class TestCsvToTsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_headers=False excludes the header row."""
        dest = tmp_path / "out.tsv"
        count = csv_to_tsv(MINIMAL_CSV, dest, include_headers=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_no_header_still_returns_correct_count(self, tmp_path: Path) -> None:
        """Without headers, still returns correct data row count."""
        dest = tmp_path / "out.tsv"
        count = csv_to_tsv(MINIMAL_CSV, dest, include_headers=False)
        assert count == 2


class TestCsvToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        csv_to_tsv(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = csv_to_tsv(str(MINIMAL_CSV), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

    def test_single_cell_csv(self, tmp_path: Path) -> None:
        """single-cell.csv produces non-empty TSV output."""
        dest = tmp_path / "out.tsv"
        csv_to_tsv(SINGLE_CELL_CSV, dest)
        assert dest.exists()
        assert len(dest.read_text(encoding="utf-8").strip()) > 0
