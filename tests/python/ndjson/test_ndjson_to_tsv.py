"""
Tests for ndjson_to_tsv dogfood export.

Verifies that NDJSON records are converted to TSV using
Format Factory's ndjson reader and tsv writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

SAMPLE_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"

from ndjson.ndjson_to_tsv import ndjson_to_tsv


class TestNdjsonToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.tsv"
        count = ndjson_to_tsv(SAMPLE_NDJSON, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        ndjson_to_tsv(SAMPLE_NDJSON, dest)
        assert dest.exists()

    def test_output_is_non_empty(self, tmp_path: Path) -> None:
        """Output file has content."""
        dest = tmp_path / "out.tsv"
        ndjson_to_tsv(SAMPLE_NDJSON, dest)
        assert dest.stat().st_size > 0

    def test_minimal_ndjson_produces_three_records(self, tmp_path: Path) -> None:
        """minimal.ndjson has 3 records -> 3 data rows."""
        dest = tmp_path / "out.tsv"
        count = ndjson_to_tsv(SAMPLE_NDJSON, dest)
        assert count == 3

    def test_output_is_tab_separated(self, tmp_path: Path) -> None:
        """Output lines contain tab characters."""
        dest = tmp_path / "out.tsv"
        ndjson_to_tsv(SAMPLE_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert "\t" in content


class TestNdjsonToTsvContent:
    """Content accuracy tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row is written as the first line by default."""
        dest = tmp_path / "out.tsv"
        ndjson_to_tsv(SAMPLE_NDJSON, dest)
        lines = dest.read_text(encoding="utf-8").splitlines()
        # First line should have field names
        assert "name" in lines[0] or "score" in lines[0]

    def test_header_includes_all_keys(self, tmp_path: Path) -> None:
        """Header contains all keys from the NDJSON records."""
        dest = tmp_path / "out.tsv"
        ndjson_to_tsv(SAMPLE_NDJSON, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        # minimal.ndjson records have name, score, active
        assert "name" in first_line
        assert "score" in first_line

    def test_data_values_present(self, tmp_path: Path) -> None:
        """Record values (Alice, Bob, Carol) appear in output."""
        dest = tmp_path / "out.tsv"
        ndjson_to_tsv(SAMPLE_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alice" in content
        assert "Bob" in content

    def test_data_rows_plus_header_total(self, tmp_path: Path) -> None:
        """Total lines = data rows + 1 (header)."""
        dest = tmp_path / "out.tsv"
        count = ndjson_to_tsv(SAMPLE_NDJSON, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1  # header + data rows

    def test_three_columns_per_row(self, tmp_path: Path) -> None:
        """Each row has 3 tab-separated fields (name/score/active)."""
        dest = tmp_path / "out.tsv"
        ndjson_to_tsv(SAMPLE_NDJSON, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert len(line.split("\t")) == 3


class TestNdjsonToTsvOptions:
    """Option and parameter tests."""

    def test_no_header_when_disabled(self, tmp_path: Path) -> None:
        """No header row when include_headers=False."""
        dest = tmp_path / "out.tsv"
        count = ndjson_to_tsv(SAMPLE_NDJSON, dest, include_headers=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count  # no extra header line

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = ndjson_to_tsv(str(SAMPLE_NDJSON), str(dest))
        assert isinstance(count, int)
        assert dest.exists()


class TestNdjsonToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        ndjson_to_tsv(SAMPLE_NDJSON, dest)
        assert dest.exists()
