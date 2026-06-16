"""test_dogfood_dif_analytics_gaps_ndjson_export.py

Dogfood export path: DIF analytics gap functions → NDJSON.

Covers: dif_is_all_string, dif_nonempty_cell_ratio, dif_avg_numeric_value,
dif_row_length_variance, dif_empty_column_count, dif_longest_row_index,
dif_total_string_length, dif_column_density.

Concrete values (minimal-2x2.dif):
  is_all_string       = False
  nonempty_cell_ratio = 1.0
  avg_numeric_value   = 70.5
  row_length_variance = 0.0
  empty_column_count  = 0
  longest_row_index   = 0
  total_string_length = 36
  column_density      = 1.0

Sprint: product-deepening-dif-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import (
    dif_is_all_string,
    dif_nonempty_cell_ratio,
    dif_avg_numeric_value,
    dif_row_length_variance,
    dif_empty_column_count,
    dif_longest_row_index,
    dif_total_string_length,
    dif_column_density,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
MINIMAL = SAMPLES_DIR / "minimal-2x2.dif"
NUMERIC = SAMPLES_DIR / "numeric-row.dif"


def _export_dif_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "is_all_string": dif_is_all_string(path),
        "nonempty_cell_ratio": dif_nonempty_cell_ratio(path),
        "avg_numeric_value": dif_avg_numeric_value(path),
        "row_length_variance": dif_row_length_variance(path),
        "empty_column_count": dif_empty_column_count(path),
        "longest_row_index": dif_longest_row_index(path),
        "total_string_length": dif_total_string_length(path),
        "column_density": dif_column_density(path),
    }


class TestDifAnalyticsGapsNdjsonExport:

    def test_minimal_is_not_all_string(self):
        rec = _export_dif_gaps_record(MINIMAL)
        assert rec["is_all_string"] is False

    def test_minimal_nonempty_cell_ratio_is_one(self):
        rec = _export_dif_gaps_record(MINIMAL)
        assert abs(rec["nonempty_cell_ratio"] - 1.0) < 0.01

    def test_minimal_avg_numeric_value(self):
        rec = _export_dif_gaps_record(MINIMAL)
        assert abs(rec["avg_numeric_value"] - 70.5) < 0.01

    def test_minimal_row_length_variance_is_zero(self):
        rec = _export_dif_gaps_record(MINIMAL)
        assert rec["row_length_variance"] == 0.0

    def test_minimal_empty_column_count_zero(self):
        rec = _export_dif_gaps_record(MINIMAL)
        assert rec["empty_column_count"] == 0

    def test_minimal_longest_row_index_zero(self):
        rec = _export_dif_gaps_record(MINIMAL)
        assert rec["longest_row_index"] == 0

    def test_minimal_total_string_length(self):
        rec = _export_dif_gaps_record(MINIMAL)
        assert rec["total_string_length"] == 36

    def test_minimal_column_density_is_one(self):
        rec = _export_dif_gaps_record(MINIMAL)
        assert abs(rec["column_density"] - 1.0) < 0.01

    def test_record_has_all_keys(self):
        rec = _export_dif_gaps_record(MINIMAL)
        for key in ["file", "is_all_string", "nonempty_cell_ratio",
                    "avg_numeric_value", "row_length_variance",
                    "empty_column_count", "longest_row_index",
                    "total_string_length", "column_density"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_dif_gaps_record(MINIMAL), _export_dif_gaps_record(NUMERIC)]
        out = tmp_path / "dif_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "column_density" in parsed

    def test_ndjson_file_key_correct(self, tmp_path):
        records = [_export_dif_gaps_record(MINIMAL)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "minimal-2x2.dif"

    def test_numeric_avg_numeric_value(self):
        rec = _export_dif_gaps_record(NUMERIC)
        assert abs(rec["avg_numeric_value"] - 2.0) < 0.01
