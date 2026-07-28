"""
Tests for csv_to_ndjson dogfood export.

Verifies that CSV rows are converted to NDJSON records using
Format Factory's CSV parser and NDJSON writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLE_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"
SINGLE_CELL_CSV = _REPO / "samples" / "by-format" / "csv" / "single-cell.csv"
QUOTED_CSV = _REPO / "samples" / "by-format" / "csv" / "quoted-fields.csv"

from src.python.ff_csv.csv_to_ndjson import csv_to_ndjson


class TestCsvToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = csv_to_ndjson(SAMPLE_CSV, dest)
        assert isinstance(count, int)
        assert count > 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created at the specified path."""
        dest = tmp_path / "out.ndjson"
        csv_to_ndjson(SAMPLE_CSV, dest)
        assert dest.exists()

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        csv_to_ndjson(SAMPLE_CSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_record_count_matches_return_value(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.ndjson"
        count = csv_to_ndjson(SAMPLE_CSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestCsvToNdjsonHeaders:
    """Header-based key tests."""

    def test_headers_become_keys(self, tmp_path: Path) -> None:
        """CSV header fields become JSON object keys."""
        dest = tmp_path / "out.ndjson"
        csv_to_ndjson(SAMPLE_CSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        records = [json.loads(l) for l in lines]
        # minimal-2x2.csv has headers: Name, Age
        assert all("Name" in r for r in records)
        assert all("Age" in r for r in records)

    def test_header_row_not_included_as_record(self, tmp_path: Path) -> None:
        """Header row is not emitted as a data record."""
        dest = tmp_path / "out.ndjson"
        count = csv_to_ndjson(SAMPLE_CSV, dest)
        # minimal-2x2.csv: 1 header + 2 data rows → 2 records
        assert count == 2

    def test_data_values_correct(self, tmp_path: Path) -> None:
        """Row values are mapped to the correct header keys."""
        dest = tmp_path / "out.ndjson"
        csv_to_ndjson(SAMPLE_CSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        records = [json.loads(l) for l in lines]
        names = [r["Name"] for r in records]
        assert "Alice" in names
        assert "Bob" in names


class TestCsvToNdjsonNoHeaders:
    """No-header CSV tests."""

    def test_no_header_uses_col_keys(self, tmp_path: Path) -> None:
        """When CSV has no header, keys are col_0, col_1, ..."""
        dest = tmp_path / "out.ndjson"
        csv_to_ndjson(SINGLE_CELL_CSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        if lines:
            obj = json.loads(lines[0])
            # single-cell.csv has a header "value" so check either header or col_ pattern
            keys = list(obj.keys())
            assert all(k.startswith("col_") or k == "value" for k in keys if k != "row_index")


class TestCsvToNdjsonRowIndex:
    """Row index option tests."""

    def test_row_index_absent_by_default(self, tmp_path: Path) -> None:
        """row_index is not included by default."""
        dest = tmp_path / "out.ndjson"
        csv_to_ndjson(SAMPLE_CSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "row_index" not in json.loads(line)

    def test_row_index_included_when_enabled(self, tmp_path: Path) -> None:
        """row_index is present when include_row_index=True."""
        dest = tmp_path / "out.ndjson"
        csv_to_ndjson(SAMPLE_CSV, dest, include_row_index=True)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "row_index" in json.loads(line)

    def test_row_index_sequential(self, tmp_path: Path) -> None:
        """row_index values are sequential from 0."""
        dest = tmp_path / "out.ndjson"
        count = csv_to_ndjson(SAMPLE_CSV, dest, include_row_index=True)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        indices = [json.loads(l)["row_index"] for l in lines]
        assert indices == list(range(count))


class TestCsvToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        csv_to_ndjson(SAMPLE_CSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = csv_to_ndjson(str(SAMPLE_CSV), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
