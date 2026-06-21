"""
tests/python/dogfood/test_dogfood_ndjson_gnumeric_tsv_final_gap_closure_ndjson_export.py

Sprint: dogfood-analytics-gap-closure-20260617
Dogfood export: NDJSON + Gnumeric + TSV analytics -> NDJSON roundtrip.
Covers 8 remaining gap-ledger open functions.
"""
from __future__ import annotations

import json
import sys
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    ndjson_string_value_count_exceeds_record_count,
    ndjson_string_value_count_minus_record_count,
)
from gnumeric.gnumeric_codec import (
    gnumeric_cell_value_range,
    gnumeric_numeric_to_string_ratio,
    gnumeric_row_col_ratio,
    gnumeric_row_count_total,
)
from tsv.tsv_parser import (
    tsv_column_count_exceeds_row_count,
    tsv_max_field_numeric_value,
)

_GNUMERIC = str(_REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric")
_TSV = str(_REPO / "samples" / "by-format" / "tsv" / "multi-column.tsv")


def _make_ndjson_with_strings(tmp_path: Path) -> str:
    """Create a temp NDJSON file with mixed string/numeric values."""
    out = str(tmp_path / "mixed.ndjson")
    records = [
        {"a": "hello", "b": "world"},
        {"a": "foo", "b": 42},
    ]
    write_ndjson(records, out)
    return out


class TestNdjsonGnumericTsvFinalGapClosureNdjsonExport:
    """8 final gap-ledger open analytics functions -> NDJSON dogfood export."""

    # --- NDJSON ---

    def test_ndjson_string_value_count_exceeds_record_count(self, tmp_path):
        nj = _make_ndjson_with_strings(tmp_path)
        # 3 string values across 2 records -> exceeds
        assert ndjson_string_value_count_exceeds_record_count(nj) is True

    def test_ndjson_string_value_count_minus_record_count(self, tmp_path):
        nj = _make_ndjson_with_strings(tmp_path)
        # 3 strings - 2 records = 1
        assert ndjson_string_value_count_minus_record_count(nj) == 1

    # --- Gnumeric ---

    def test_gnumeric_cell_value_range(self):
        val = gnumeric_cell_value_range(_GNUMERIC)
        assert isinstance(val, float)
        assert val >= 0.0

    def test_gnumeric_numeric_to_string_ratio(self):
        val = gnumeric_numeric_to_string_ratio(_GNUMERIC)
        assert isinstance(val, float)
        assert val >= 0.0

    def test_gnumeric_row_col_ratio(self):
        val = gnumeric_row_col_ratio(_GNUMERIC)
        assert isinstance(val, float)
        assert val >= 0.0

    def test_gnumeric_row_count_total(self):
        val = gnumeric_row_count_total(_GNUMERIC)
        assert isinstance(val, int)
        assert val >= 0

    # --- TSV ---

    def test_tsv_column_count_exceeds_row_count(self):
        # multi-column.tsv has more columns than rows
        assert tsv_column_count_exceeds_row_count(_TSV) is True

    def test_tsv_max_field_numeric_value(self):
        val = tsv_max_field_numeric_value(_TSV)
        assert abs(val - 95.5) < 0.001

    # --- NDJSON roundtrip of all results ---

    def test_ndjson_roundtrip(self, tmp_path):
        nj = _make_ndjson_with_strings(tmp_path)
        out = tmp_path / "gap_closure.ndjson"
        records = [
            {"fn": "ndjson_string_value_count_exceeds_record_count",
             "value": ndjson_string_value_count_exceeds_record_count(nj)},
            {"fn": "ndjson_string_value_count_minus_record_count",
             "value": ndjson_string_value_count_minus_record_count(nj)},
            {"fn": "gnumeric_cell_value_range",
             "value": gnumeric_cell_value_range(_GNUMERIC)},
            {"fn": "gnumeric_row_col_ratio",
             "value": gnumeric_row_col_ratio(_GNUMERIC)},
            {"fn": "tsv_max_field_numeric_value",
             "value": tsv_max_field_numeric_value(_TSV)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 5
        assert loaded[0]["value"] is True
        assert loaded[1]["value"] == 1
        assert loaded[4]["value"] == 95.5
