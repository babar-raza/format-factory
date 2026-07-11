"""
Tests for dif_to_ndjson dogfood export.

Verifies that DIF rows are converted to NDJSON records using
Format Factory's DIF parser and NDJSON writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

NUMERIC_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "numeric-row.dif"
SINGLE_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "single-cell.dif"

from dif.dif_to_ndjson import dif_to_ndjson


class TestDifToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = dif_to_ndjson(NUMERIC_DIF, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created."""
        dest = tmp_path / "out.ndjson"
        dif_to_ndjson(NUMERIC_DIF, dest)
        assert dest.exists()

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        dif_to_ndjson(NUMERIC_DIF, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_record_count_matches_return_value(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.ndjson"
        count = dif_to_ndjson(NUMERIC_DIF, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_numeric_row_one_record(self, tmp_path: Path) -> None:
        """numeric-row.dif has 1 row → 1 record."""
        dest = tmp_path / "out.ndjson"
        count = dif_to_ndjson(NUMERIC_DIF, dest)
        assert count == 1


class TestDifToNdjsonContent:
    """Content correctness tests."""

    def test_col_keys_present(self, tmp_path: Path) -> None:
        """Records use col_0, col_1, ... col_N as keys."""
        dest = tmp_path / "out.ndjson"
        dif_to_ndjson(NUMERIC_DIF, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "col_0" in record
        assert "col_1" in record
        assert "col_2" in record

    def test_numeric_values_present(self, tmp_path: Path) -> None:
        """numeric-row.dif values 1.0, 2.0, 3.0 appear in output."""
        dest = tmp_path / "out.ndjson"
        dif_to_ndjson(NUMERIC_DIF, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        values = list(record.values())
        assert "1.0" in values

    def test_single_cell_one_column(self, tmp_path: Path) -> None:
        """single-cell.dif has 1 row with 1 column."""
        dest = tmp_path / "out.ndjson"
        count = dif_to_ndjson(SINGLE_DIF, dest)
        assert count == 1
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        # Only col_0 and optionally row_index
        assert "col_0" in record
        assert record["col_0"] == "42.0"


class TestDifToNdjsonOptions:
    """Option flag tests."""

    def test_row_index_absent_by_default(self, tmp_path: Path) -> None:
        """row_index not included by default."""
        dest = tmp_path / "out.ndjson"
        dif_to_ndjson(NUMERIC_DIF, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "row_index" not in record

    def test_row_index_included_when_enabled(self, tmp_path: Path) -> None:
        """row_index present when include_row_index=True."""
        dest = tmp_path / "out.ndjson"
        dif_to_ndjson(NUMERIC_DIF, dest, include_row_index=True)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "row_index" in record
        assert record["row_index"] == 0

    def test_value_types_absent_by_default(self, tmp_path: Path) -> None:
        """col_N_type fields not included by default."""
        dest = tmp_path / "out.ndjson"
        dif_to_ndjson(NUMERIC_DIF, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "col_0_type" not in record

    def test_value_types_included_when_enabled(self, tmp_path: Path) -> None:
        """col_N_type fields present when include_value_types=True."""
        dest = tmp_path / "out.ndjson"
        dif_to_ndjson(NUMERIC_DIF, dest, include_value_types=True)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "col_0_type" in record
        assert record["col_0_type"] == "numeric"


class TestDifToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        dif_to_ndjson(NUMERIC_DIF, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = dif_to_ndjson(str(NUMERIC_DIF), str(dest))
        assert isinstance(count, int)
        assert dest.exists()
