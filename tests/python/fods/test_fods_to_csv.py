"""
Tests for fods_to_csv dogfood export.

Verifies that FODS spreadsheet rows are converted to CSV using
Format Factory's FODS parser and CSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
SIMPLE_FODS = _REPO / "samples" / "by-format" / "fods" / "valid" / "simple.fods"
TYPED_FODS = _REPO / "samples" / "by-format" / "fods" / "typed-values-basic.fods"
MULTI_SHEET_FODS = _REPO / "samples" / "by-format" / "fods" / "multi-sheet-basic.fods"

from fods.fods_to_csv import fods_to_csv


class TestFodsToCsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.csv"
        count = fods_to_csv(MINIMAL_FODS, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        fods_to_csv(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_output_nonempty_for_simple(self, tmp_path: Path) -> None:
        """Simple FODS with 2 rows produces non-empty CSV."""
        dest = tmp_path / "out.csv"
        count = fods_to_csv(SIMPLE_FODS, dest)
        assert count == 2
        content = dest.read_text(encoding="utf-8")
        assert len(content.strip()) > 0

    def test_row_count_matches_return_value(self, tmp_path: Path) -> None:
        """Line count in output matches return value."""
        dest = tmp_path / "out.csv"
        count = fods_to_csv(SIMPLE_FODS, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestFodsToCsvContent:
    """Content correctness tests."""

    def test_simple_fods_has_header_values(self, tmp_path: Path) -> None:
        """simple.fods first row contains Name and Value headers."""
        dest = tmp_path / "out.csv"
        fods_to_csv(SIMPLE_FODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Name" in content
        assert "Value" in content

    def test_simple_fods_has_data_values(self, tmp_path: Path) -> None:
        """simple.fods data row contains Alpha and 42."""
        dest = tmp_path / "out.csv"
        fods_to_csv(SIMPLE_FODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alpha" in content
        assert "42" in content

    def test_typed_values_float_converted_to_string(self, tmp_path: Path) -> None:
        """Float cell values are converted to string in the CSV output."""
        dest = tmp_path / "out.csv"
        fods_to_csv(TYPED_FODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "42.5" in content

    def test_typed_values_row_count(self, tmp_path: Path) -> None:
        """typed-values-basic.fods has 4 rows → 4 CSV lines."""
        dest = tmp_path / "out.csv"
        count = fods_to_csv(TYPED_FODS, dest)
        assert count == 4


class TestFodsToCsvOptions:
    """Option and flag tests."""

    def test_skip_empty_rows_true_by_default(self, tmp_path: Path) -> None:
        """skip_empty_rows=True by default does not add blank lines."""
        dest = tmp_path / "out.csv"
        count = fods_to_csv(SIMPLE_FODS, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_sheet_index_default_zero(self, tmp_path: Path) -> None:
        """Default sheet_index=0 exports the first sheet."""
        dest = tmp_path / "out.csv"
        count = fods_to_csv(SIMPLE_FODS, dest, sheet_index=0)
        assert count > 0


class TestFodsToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        fods_to_csv(SIMPLE_FODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = fods_to_csv(str(SIMPLE_FODS), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

    def test_minimal_spreadsheet_single_row(self, tmp_path: Path) -> None:
        """minimal-spreadsheet.fods (1 row) produces 1 CSV line."""
        dest = tmp_path / "out.csv"
        count = fods_to_csv(MINIMAL_FODS, dest)
        assert count == 1
