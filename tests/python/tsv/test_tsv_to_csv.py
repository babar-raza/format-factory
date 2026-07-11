"""
Tests for tsv_to_csv dogfood export.

Verifies that TSV rows are converted to CSV using
Format Factory's TSV parser and CSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
SINGLE_CELL_TSV = _REPO / "samples" / "by-format" / "tsv" / "single-cell.tsv"
MULTI_COL_TSV = _REPO / "samples" / "by-format" / "tsv" / "multi-column.tsv"

from tsv.tsv_to_csv import tsv_to_csv


class TestTsvToCsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.csv"
        count = tsv_to_csv(MINIMAL_TSV, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        tsv_to_csv(MINIMAL_TSV, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """CSV output is non-empty."""
        dest = tmp_path / "out.csv"
        tsv_to_csv(MINIMAL_TSV, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_minimal_tsv_returns_two_rows(self, tmp_path: Path) -> None:
        """minimal-2x2.tsv with 2 data rows → count of 2."""
        dest = tmp_path / "out.csv"
        count = tsv_to_csv(MINIMAL_TSV, dest)
        assert count == 2


class TestTsvToCsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header from TSV appears as first CSV line."""
        dest = tmp_path / "out.csv"
        tsv_to_csv(MINIMAL_TSV, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "Name" in first_line

    def test_header_uses_commas(self, tmp_path: Path) -> None:
        """CSV output uses commas (not tabs) as delimiter."""
        dest = tmp_path / "out.csv"
        tsv_to_csv(MINIMAL_TSV, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "," in first_line
        assert "\t" not in first_line

    def test_data_values_in_output(self, tmp_path: Path) -> None:
        """TSV data values appear in CSV output."""
        dest = tmp_path / "out.csv"
        tsv_to_csv(MINIMAL_TSV, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alice" in content
        assert "Bob" in content

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.csv"
        count = tsv_to_csv(MINIMAL_TSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_data_rows_use_commas(self, tmp_path: Path) -> None:
        """Data rows are comma-delimited, not tab-delimited."""
        dest = tmp_path / "out.csv"
        tsv_to_csv(MINIMAL_TSV, dest)
        lines = dest.read_text(encoding="utf-8").splitlines()
        for line in lines[1:]:
            if line.strip():
                assert "," in line
                assert "\t" not in line


class TestTsvToCsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_headers=False excludes the header row."""
        dest = tmp_path / "out.csv"
        count = tsv_to_csv(MINIMAL_TSV, dest, include_headers=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_no_header_returns_correct_count(self, tmp_path: Path) -> None:
        """Without headers, returns correct data row count."""
        dest = tmp_path / "out.csv"
        count = tsv_to_csv(MINIMAL_TSV, dest, include_headers=False)
        assert count == 2


class TestTsvToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        tsv_to_csv(MINIMAL_TSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = tsv_to_csv(str(MINIMAL_TSV), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

    def test_single_cell_tsv(self, tmp_path: Path) -> None:
        """single-cell.tsv produces non-empty CSV output."""
        dest = tmp_path / "out.csv"
        tsv_to_csv(SINGLE_CELL_TSV, dest)
        assert dest.exists()
        assert len(dest.read_text(encoding="utf-8").strip()) > 0
