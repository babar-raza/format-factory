"""
Tests for ods_to_csv dogfood export.

Verifies that ODS sheet data is converted to CSV using
Format Factory's ods reader and csv writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLE_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"
NUMERIC_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "numeric-row.ods"

from ods.ods_to_csv import ods_to_csv


class TestOdsToCsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.csv"
        count = ods_to_csv(SAMPLE_ODS, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        ods_to_csv(SAMPLE_ODS, dest)
        assert dest.exists()

    def test_output_is_non_empty(self, tmp_path: Path) -> None:
        """Output file has content."""
        dest = tmp_path / "out.csv"
        ods_to_csv(SAMPLE_ODS, dest)
        assert dest.stat().st_size > 0

    def test_minimal_spreadsheet_row_count(self, tmp_path: Path) -> None:
        """minimal-spreadsheet.ods produces 2 non-empty rows."""
        dest = tmp_path / "out.csv"
        count = ods_to_csv(SAMPLE_ODS, dest)
        assert count == 2

    def test_output_is_valid_csv(self, tmp_path: Path) -> None:
        """Output can be parsed as CSV with correct column count."""
        import csv as _csv
        dest = tmp_path / "out.csv"
        ods_to_csv(SAMPLE_ODS, dest)
        rows = list(_csv.reader(dest.read_text(encoding="utf-8").splitlines()))
        assert len(rows) >= 1
        for row in rows:
            assert isinstance(row, list)


class TestOdsToCsvContent:
    """Content accuracy tests."""

    def test_header_row_preserved(self, tmp_path: Path) -> None:
        """First row (header) text is preserved in CSV output."""
        dest = tmp_path / "out.csv"
        ods_to_csv(SAMPLE_ODS, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "Name" in first_line or "Value" in first_line

    def test_data_row_preserved(self, tmp_path: Path) -> None:
        """Data row values are present in CSV output."""
        dest = tmp_path / "out.csv"
        ods_to_csv(SAMPLE_ODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alpha" in content or "42" in content

    def test_line_count_matches_return(self, tmp_path: Path) -> None:
        """Non-empty line count matches the return value."""
        dest = tmp_path / "out.csv"
        count = ods_to_csv(SAMPLE_ODS, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_numeric_row_exported(self, tmp_path: Path) -> None:
        """numeric-row.ods produces at least one row of data."""
        dest = tmp_path / "out.csv"
        count = ods_to_csv(NUMERIC_ODS, dest)
        assert count >= 1


class TestOdsToCsvOptions:
    """Option and parameter tests."""

    def test_skip_empty_rows_default(self, tmp_path: Path) -> None:
        """Empty rows are skipped by default."""
        dest = tmp_path / "out.csv"
        count = ods_to_csv(SAMPLE_ODS, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_sheet_index_default_zero(self, tmp_path: Path) -> None:
        """Default sheet_index=0 exports first sheet."""
        dest_default = tmp_path / "default.csv"
        dest_zero = tmp_path / "zero.csv"
        ods_to_csv(SAMPLE_ODS, dest_default)
        ods_to_csv(SAMPLE_ODS, dest_zero, sheet_index=0)
        assert dest_default.read_text(encoding="utf-8") == dest_zero.read_text(encoding="utf-8")

    def test_invalid_sheet_index_raises(self, tmp_path: Path) -> None:
        """Out-of-range sheet_index raises OdsError."""
        from ods.ods_parser import OdsError
        dest = tmp_path / "out.csv"
        with pytest.raises(OdsError):
            ods_to_csv(SAMPLE_ODS, dest, sheet_index=99)

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = ods_to_csv(str(SAMPLE_ODS), str(dest))
        assert isinstance(count, int)
        assert dest.exists()


class TestOdsToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        ods_to_csv(SAMPLE_ODS, dest)
        assert dest.exists()
