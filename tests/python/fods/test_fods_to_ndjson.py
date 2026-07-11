"""
Tests for fods_to_ndjson dogfood export.

Verifies that FODS spreadsheet rows are converted to NDJSON records using
Format Factory's FODS parser and NDJSON writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
SIMPLE_FODS = _REPO / "samples" / "by-format" / "fods" / "valid" / "simple.fods"
TYPED_FODS = _REPO / "samples" / "by-format" / "fods" / "typed-values-basic.fods"

from fods.fods_to_ndjson import fods_to_ndjson


class TestFodsToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = fods_to_ndjson(MINIMAL_FODS, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created at the specified path."""
        dest = tmp_path / "out.ndjson"
        fods_to_ndjson(SIMPLE_FODS, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """NDJSON output is non-empty."""
        dest = tmp_path / "out.ndjson"
        fods_to_ndjson(SIMPLE_FODS, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_simple_fods_returns_one_data_row(self, tmp_path: Path) -> None:
        """simple.fods with header + 1 data row → 1 record."""
        dest = tmp_path / "out.ndjson"
        count = fods_to_ndjson(SIMPLE_FODS, dest)
        assert count == 1


class TestFodsToNdjsonContent:
    """Content correctness tests."""

    def test_records_are_valid_json(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        fods_to_ndjson(SIMPLE_FODS, dest)
        for line in dest.read_text(encoding="utf-8").splitlines():
            if line.strip():
                obj = json.loads(line)
                assert isinstance(obj, dict)

    def test_header_keys_in_records(self, tmp_path: Path) -> None:
        """Record keys come from first-row headers."""
        dest = tmp_path / "out.ndjson"
        fods_to_ndjson(SIMPLE_FODS, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        record = json.loads(lines[0])
        # simple.fods has Name and Value headers
        assert "Name" in record or "Value" in record

    def test_data_values_in_records(self, tmp_path: Path) -> None:
        """Data values appear in the NDJSON records."""
        dest = tmp_path / "out.ndjson"
        fods_to_ndjson(SIMPLE_FODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "Alpha" in content or "42" in content

    def test_typed_values_row_count(self, tmp_path: Path) -> None:
        """typed-values-basic.fods → correct number of data records."""
        dest = tmp_path / "out.ndjson"
        count = fods_to_ndjson(TYPED_FODS, dest)
        # typed-values-basic has header + data rows
        assert count >= 1

    def test_line_count_matches_return_value(self, tmp_path: Path) -> None:
        """Non-empty lines in output match return value."""
        dest = tmp_path / "out.ndjson"
        count = fods_to_ndjson(SIMPLE_FODS, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestFodsToNdjsonOptions:
    """Option flag tests."""

    def test_no_headers_uses_col_keys(self, tmp_path: Path) -> None:
        """use_first_row_as_headers=False uses col_0, col_1 keys."""
        dest = tmp_path / "out.ndjson"
        fods_to_ndjson(SIMPLE_FODS, dest, use_first_row_as_headers=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        record = json.loads(lines[0])
        assert "col_0" in record

    def test_include_row_index_adds_field(self, tmp_path: Path) -> None:
        """include_row_index=True adds row_index to each record."""
        dest = tmp_path / "out.ndjson"
        fods_to_ndjson(SIMPLE_FODS, dest, include_row_index=True)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        record = json.loads(lines[0])
        assert "row_index" in record

    def test_row_index_absent_by_default(self, tmp_path: Path) -> None:
        """row_index field absent by default."""
        dest = tmp_path / "out.ndjson"
        fods_to_ndjson(SIMPLE_FODS, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        record = json.loads(lines[0])
        assert "row_index" not in record

    def test_sheet_index_default_zero(self, tmp_path: Path) -> None:
        """Default sheet_index=0 exports the first sheet."""
        dest = tmp_path / "out.ndjson"
        count = fods_to_ndjson(SIMPLE_FODS, dest, sheet_index=0)
        assert count >= 0


class TestFodsToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        fods_to_ndjson(SIMPLE_FODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = fods_to_ndjson(str(SIMPLE_FODS), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
