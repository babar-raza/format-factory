"""
Tests for gnumeric_to_ndjson dogfood export.

Verifies that Gnumeric spreadsheet rows are converted to NDJSON records using
Format Factory's Gnumeric codec and NDJSON writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_GNM = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
MULTI_CELL_GNM = _REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric"

from gnumeric.gnumeric_to_ndjson import gnumeric_to_ndjson


class TestGnumericToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = gnumeric_to_ndjson(MULTI_CELL_GNM, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created."""
        dest = tmp_path / "out.ndjson"
        gnumeric_to_ndjson(MULTI_CELL_GNM, dest)
        assert dest.exists()

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        gnumeric_to_ndjson(MULTI_CELL_GNM, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_record_count_matches_return_value(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.ndjson"
        count = gnumeric_to_ndjson(MULTI_CELL_GNM, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestGnumericToNdjsonHeaders:
    """Header row handling tests."""

    def test_first_row_becomes_keys(self, tmp_path: Path) -> None:
        """When use_first_row_as_headers=True, first row provides JSON keys."""
        dest = tmp_path / "out.ndjson"
        gnumeric_to_ndjson(MULTI_CELL_GNM, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        records = [json.loads(l) for l in lines]
        # multi-cell-basic has headers: Name, Score
        assert all("Name" in r for r in records)
        assert all("Score" in r for r in records)

    def test_header_row_not_included_as_record(self, tmp_path: Path) -> None:
        """Header row is not emitted as a data record."""
        dest = tmp_path / "out.ndjson"
        count = gnumeric_to_ndjson(MULTI_CELL_GNM, dest)
        # multi-cell-basic: 2 rows total (1 header + 1 data) → 1 record
        assert count == 1

    def test_data_values_correct(self, tmp_path: Path) -> None:
        """Data row values are mapped to the correct header keys."""
        dest = tmp_path / "out.ndjson"
        gnumeric_to_ndjson(MULTI_CELL_GNM, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        record = json.loads(lines[0])
        assert record["Name"] == "Alice"
        assert record["Score"] == "42"

    def test_no_headers_uses_col_keys(self, tmp_path: Path) -> None:
        """When use_first_row_as_headers=False, keys are col_0, col_1, ..."""
        dest = tmp_path / "out.ndjson"
        gnumeric_to_ndjson(MULTI_CELL_GNM, dest, use_first_row_as_headers=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            for k in json.loads(line):
                assert k.startswith("col_") or k == "row_index"

    def test_minimal_single_cell_no_header(self, tmp_path: Path) -> None:
        """minimal-spreadsheet (1 row) with no-header emits 1 record."""
        dest = tmp_path / "out.ndjson"
        count = gnumeric_to_ndjson(MINIMAL_GNM, dest, use_first_row_as_headers=False)
        assert count == 1


class TestGnumericToNdjsonRowIndex:
    """Row index option tests."""

    def test_row_index_absent_by_default(self, tmp_path: Path) -> None:
        """row_index not included by default."""
        dest = tmp_path / "out.ndjson"
        gnumeric_to_ndjson(MULTI_CELL_GNM, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "row_index" not in json.loads(line)

    def test_row_index_included_when_enabled(self, tmp_path: Path) -> None:
        """row_index present when include_row_index=True."""
        dest = tmp_path / "out.ndjson"
        gnumeric_to_ndjson(MULTI_CELL_GNM, dest, include_row_index=True)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "row_index" in json.loads(line)


class TestGnumericToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        gnumeric_to_ndjson(MULTI_CELL_GNM, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = gnumeric_to_ndjson(str(MULTI_CELL_GNM), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
