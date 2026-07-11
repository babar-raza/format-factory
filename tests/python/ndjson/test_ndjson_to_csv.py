"""
Tests for ndjson_to_csv dogfood export.

Verifies that NDJSON records are converted to CSV rows using
Format Factory's NDJSON reader and CSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"

from ndjson.ndjson_to_csv import ndjson_to_csv


class TestNdjsonToCsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.csv"
        count = ndjson_to_csv(MINIMAL_NDJSON, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        ndjson_to_csv(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """CSV output is non-empty."""
        dest = tmp_path / "out.csv"
        ndjson_to_csv(MINIMAL_NDJSON, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_minimal_ndjson_returns_three_rows(self, tmp_path: Path) -> None:
        """minimal.ndjson with 3 records → 3 data rows."""
        dest = tmp_path / "out.csv"
        count = ndjson_to_csv(MINIMAL_NDJSON, dest)
        assert count == 3


class TestNdjsonToCsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row is written as the first line by default."""
        dest = tmp_path / "out.csv"
        ndjson_to_csv(MINIMAL_NDJSON, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "name" in first_line

    def test_header_contains_all_keys(self, tmp_path: Path) -> None:
        """Header row contains name, score, active columns."""
        dest = tmp_path / "out.csv"
        ndjson_to_csv(MINIMAL_NDJSON, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "score" in first_line
        assert "active" in first_line

    def test_data_values_in_output(self, tmp_path: Path) -> None:
        """Record values appear in the CSV output."""
        dest = tmp_path / "out.csv"
        ndjson_to_csv(MINIMAL_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alice" in content
        assert "Bob" in content
        assert "Carol" in content

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.csv"
        count = ndjson_to_csv(MINIMAL_NDJSON, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_numeric_values_converted_to_string(self, tmp_path: Path) -> None:
        """Numeric values (score) appear as strings in the CSV."""
        dest = tmp_path / "out.csv"
        ndjson_to_csv(MINIMAL_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert "95" in content
        assert "82" in content


class TestNdjsonToCsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_headers=False excludes the header row."""
        dest = tmp_path / "out.csv"
        count = ndjson_to_csv(MINIMAL_NDJSON, dest, include_headers=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_no_header_line_count_equals_row_count(self, tmp_path: Path) -> None:
        """Without header, line count equals data row count."""
        dest = tmp_path / "out.csv"
        count = ndjson_to_csv(MINIMAL_NDJSON, dest, include_headers=False)
        assert count == 3


class TestNdjsonToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        ndjson_to_csv(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = ndjson_to_csv(str(MINIMAL_NDJSON), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
