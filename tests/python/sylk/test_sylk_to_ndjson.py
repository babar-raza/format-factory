"""
Tests for sylk_to_ndjson dogfood export.

Verifies that SYLK spreadsheet rows are converted to NDJSON records using
Format Factory's SYLK parser and NDJSON writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
NUMERIC_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "numeric-row.slk"
SINGLE_SYLK = _REPO / "samples" / "by-format" / "sylk" / "valid" / "single-cell.slk"

from sylk.sylk_to_ndjson import sylk_to_ndjson


class TestSylkToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = sylk_to_ndjson(MINIMAL_SYLK, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created."""
        dest = tmp_path / "out.ndjson"
        sylk_to_ndjson(MINIMAL_SYLK, dest)
        assert dest.exists()

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        sylk_to_ndjson(MINIMAL_SYLK, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_record_count_matches_return_value(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.ndjson"
        count = sylk_to_ndjson(MINIMAL_SYLK, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestSylkToNdjsonHeaders:
    """Header row handling tests."""

    def test_first_row_becomes_keys(self, tmp_path: Path) -> None:
        """When use_first_row_as_headers=True, row 1 provides JSON keys."""
        dest = tmp_path / "out.ndjson"
        sylk_to_ndjson(MINIMAL_SYLK, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        records = [json.loads(l) for l in lines]
        # minimal-2x2.slk headers: Name, Value
        assert all("Name" in r for r in records)
        assert all("Value" in r for r in records)

    def test_header_row_not_included_as_record(self, tmp_path: Path) -> None:
        """Header row is not emitted as a data record."""
        dest = tmp_path / "out.ndjson"
        count = sylk_to_ndjson(MINIMAL_SYLK, dest)
        # minimal-2x2.slk: 2 rows (1 header + 1 data) → 1 record
        assert count == 1

    def test_data_values_correct(self, tmp_path: Path) -> None:
        """Data row values mapped to correct header keys."""
        dest = tmp_path / "out.ndjson"
        sylk_to_ndjson(MINIMAL_SYLK, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert record["Name"] == "Alpha"
        assert record["Value"] == "42"

    def test_no_headers_uses_col_keys(self, tmp_path: Path) -> None:
        """When use_first_row_as_headers=False, keys are col_0, col_1, ..."""
        dest = tmp_path / "out.ndjson"
        sylk_to_ndjson(NUMERIC_SYLK, dest, use_first_row_as_headers=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            for k in json.loads(line):
                assert k.startswith("col_") or k == "row_index"

    def test_numeric_row_no_header_one_record(self, tmp_path: Path) -> None:
        """numeric-row.slk with no-header emits 1 record with 3 columns."""
        dest = tmp_path / "out.ndjson"
        count = sylk_to_ndjson(NUMERIC_SYLK, dest, use_first_row_as_headers=False)
        assert count == 1
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "col_0" in record and "col_1" in record and "col_2" in record


class TestSylkToNdjsonRowIndex:
    """Row index option tests."""

    def test_row_index_absent_by_default(self, tmp_path: Path) -> None:
        """row_index not included by default."""
        dest = tmp_path / "out.ndjson"
        sylk_to_ndjson(MINIMAL_SYLK, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "row_index" not in record

    def test_row_index_included_when_enabled(self, tmp_path: Path) -> None:
        """row_index present when include_row_index=True."""
        dest = tmp_path / "out.ndjson"
        sylk_to_ndjson(MINIMAL_SYLK, dest, include_row_index=True)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "row_index" in record
        assert record["row_index"] == 2  # SYLK uses 1-based; data row is row 2


class TestSylkToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        sylk_to_ndjson(MINIMAL_SYLK, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = sylk_to_ndjson(str(MINIMAL_SYLK), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
