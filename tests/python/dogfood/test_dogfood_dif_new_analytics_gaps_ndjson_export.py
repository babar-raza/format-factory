"""test_dogfood_dif_new_analytics_gaps_ndjson_export.py

Dogfood export path: DIF new analytics gap functions -> NDJSON.

Covers: dif_tuple_count, dif_is_single_row, dif_is_multi_vector,
dif_string_value_count, dif_numeric_cell_ratio, dif_nonempty_row_ratio,
dif_total_cell_length, dif_numeric_sum.

Concrete values (minimal-2x2.dif):
  tuple_count         = 2
  is_single_row       = True
  is_multi_vector     = True
  string_value_count  = 2
  numeric_cell_ratio  = 0.25
  nonempty_row_ratio  = 1.0
  total_cell_length   = 36
  numeric_sum         = 141.0

Concrete values (numeric-row.dif):
  tuple_count         = 1
  string_value_count  = 0
  numeric_cell_ratio  = 1.0
  total_cell_length   = 9

Sprint: product-deepening-dif-new-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import (
    dif_tuple_count,
    dif_is_single_row,
    dif_is_multi_vector,
    dif_string_value_count,
    dif_numeric_cell_ratio,
    dif_nonempty_row_ratio,
    dif_total_cell_length,
    dif_numeric_sum,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
MINIMAL_2X2 = SAMPLES_DIR / "minimal-2x2.dif"
NUMERIC_ROW = SAMPLES_DIR / "numeric-row.dif"


def _export_dif_new_record(path: Path) -> dict:
    return {
        "file": path.name,
        "tuple_count": dif_tuple_count(path),
        "is_single_row": dif_is_single_row(path),
        "is_multi_vector": dif_is_multi_vector(path),
        "string_value_count": dif_string_value_count(path),
        "numeric_cell_ratio": dif_numeric_cell_ratio(path),
        "nonempty_row_ratio": dif_nonempty_row_ratio(path),
        "total_cell_length": dif_total_cell_length(path),
        "numeric_sum": dif_numeric_sum(path),
    }


class TestDifNewAnalyticsGapsNdjsonExport:

    def test_minimal_tuple_count_is_two(self):
        rec = _export_dif_new_record(MINIMAL_2X2)
        assert rec["tuple_count"] == 2

    def test_numeric_row_tuple_count_is_one(self):
        rec = _export_dif_new_record(NUMERIC_ROW)
        assert rec["tuple_count"] == 1

    def test_minimal_is_single_row(self):
        rec = _export_dif_new_record(MINIMAL_2X2)
        assert rec["is_single_row"] is True

    def test_minimal_is_multi_vector(self):
        rec = _export_dif_new_record(MINIMAL_2X2)
        assert rec["is_multi_vector"] is True

    def test_minimal_string_value_count_is_two(self):
        rec = _export_dif_new_record(MINIMAL_2X2)
        assert rec["string_value_count"] == 2

    def test_numeric_row_string_value_count_zero(self):
        rec = _export_dif_new_record(NUMERIC_ROW)
        assert rec["string_value_count"] == 0

    def test_minimal_numeric_cell_ratio(self):
        rec = _export_dif_new_record(MINIMAL_2X2)
        assert abs(rec["numeric_cell_ratio"] - 0.25) < 0.01

    def test_numeric_row_numeric_cell_ratio_one(self):
        rec = _export_dif_new_record(NUMERIC_ROW)
        assert abs(rec["numeric_cell_ratio"] - 1.0) < 0.01

    def test_minimal_total_cell_length(self):
        rec = _export_dif_new_record(MINIMAL_2X2)
        assert rec["total_cell_length"] == 36

    def test_record_has_all_keys(self):
        rec = _export_dif_new_record(MINIMAL_2X2)
        for key in ["file", "tuple_count", "is_single_row", "is_multi_vector",
                    "string_value_count", "numeric_cell_ratio", "nonempty_row_ratio",
                    "total_cell_length", "numeric_sum"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_dif_new_record(MINIMAL_2X2), _export_dif_new_record(NUMERIC_ROW)]
        out = tmp_path / "dif_new_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "tuple_count" in parsed

    def test_minimal_numeric_sum(self):
        rec = _export_dif_new_record(MINIMAL_2X2)
        assert abs(rec["numeric_sum"] - 141.0) < 1.0
