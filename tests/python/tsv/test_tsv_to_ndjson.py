"""
Tests for tsv_to_ndjson dogfood export.

Verifies that TSV rows are converted to NDJSON records using
Format Factory's tsv reader and ndjson writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

MINIMAL_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
MULTI_COL_TSV = _REPO / "samples" / "by-format" / "tsv" / "multi-column.tsv"

from tsv.tsv_to_ndjson import tsv_to_ndjson


class TestTsvToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = tsv_to_ndjson(MINIMAL_TSV, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created at the specified path."""
        dest = tmp_path / "out.ndjson"
        tsv_to_ndjson(MINIMAL_TSV, dest)
        assert dest.exists()

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        tsv_to_ndjson(MINIMAL_TSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_minimal_2x2_produces_two_records(self, tmp_path: Path) -> None:
        """minimal-2x2.tsv (2 data rows) produces 2 NDJSON records."""
        dest = tmp_path / "out.ndjson"
        count = tsv_to_ndjson(MINIMAL_TSV, dest)
        assert count == 2


class TestTsvToNdjsonContent:
    """Content accuracy tests."""

    def test_header_values_become_keys(self, tmp_path: Path) -> None:
        """TSV header values (Name, Age) become NDJSON record keys."""
        dest = tmp_path / "out.ndjson"
        tsv_to_ndjson(MINIMAL_TSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        rec = json.loads(lines[0])
        assert "Name" in rec
        assert "Age" in rec

    def test_data_values_preserved(self, tmp_path: Path) -> None:
        """TSV data values (Alice, 30) appear as record values."""
        dest = tmp_path / "out.ndjson"
        tsv_to_ndjson(MINIMAL_TSV, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alice" in content
        assert "30" in content

    def test_record_count_matches_return(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.ndjson"
        count = tsv_to_ndjson(MINIMAL_TSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_all_records_have_same_keys(self, tmp_path: Path) -> None:
        """All records share the same set of keys (from TSV headers)."""
        dest = tmp_path / "out.ndjson"
        tsv_to_ndjson(MINIMAL_TSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        if len(lines) > 1:
            key_sets = [set(json.loads(l).keys()) for l in lines]
            assert all(ks == key_sets[0] for ks in key_sets)


class TestTsvToNdjsonOptions:
    """Option and parameter tests."""

    def test_row_index_included_when_enabled(self, tmp_path: Path) -> None:
        """row_index field present when include_row_index=True."""
        dest = tmp_path / "out.ndjson"
        tsv_to_ndjson(MINIMAL_TSV, dest, include_row_index=True)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert all("row_index" in json.loads(l) for l in lines)

    def test_row_index_absent_by_default(self, tmp_path: Path) -> None:
        """row_index field absent by default."""
        dest = tmp_path / "out.ndjson"
        tsv_to_ndjson(MINIMAL_TSV, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert all("row_index" not in json.loads(l) for l in lines)

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = tsv_to_ndjson(str(MINIMAL_TSV), str(dest))
        assert isinstance(count, int)
        assert dest.exists()


class TestTsvToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        tsv_to_ndjson(MINIMAL_TSV, dest)
        assert dest.exists()
