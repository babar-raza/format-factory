"""test_dogfood_tsv_analytics_gaps_ndjson_export.py

Dogfood export path: TSV analytics gap functions → NDJSON.

Covers: tsv_has_duplicates, tsv_empty_column_count, tsv_longest_row_index,
tsv_max_row_cell_count, tsv_distinct_value_ratio, tsv_column_value_variance,
tsv_field_length_sum, tsv_cell_to_row_ratio.

Concrete values (minimal-2x2.tsv):
  has_duplicates       = False
  empty_column_count   = 0
  longest_row_index    = 0
  max_row_cell_count   = 2
  distinct_value_ratio = 1.0
  field_length_sum     = 12
  cell_to_row_ratio    = 2.0

Sprint: product-deepening-tsv-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    tsv_has_duplicates,
    tsv_empty_column_count,
    tsv_longest_row_index,
    tsv_max_row_cell_count,
    tsv_distinct_value_ratio,
    tsv_column_value_variance,
    tsv_field_length_sum,
    tsv_cell_to_row_ratio,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "tsv"
MINIMAL = SAMPLES_DIR / "minimal-2x2.tsv"
MULTI = SAMPLES_DIR / "multi-column.tsv"


def _export_tsv_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "has_duplicates": tsv_has_duplicates(path),
        "empty_column_count": tsv_empty_column_count(path),
        "longest_row_index": tsv_longest_row_index(path),
        "max_row_cell_count": tsv_max_row_cell_count(path),
        "distinct_value_ratio": tsv_distinct_value_ratio(path),
        "column_value_variance": tsv_column_value_variance(path),
        "field_length_sum": tsv_field_length_sum(path),
        "cell_to_row_ratio": tsv_cell_to_row_ratio(path),
    }


class TestTsvAnalyticsGapsNdjsonExport:

    def test_minimal_no_duplicates(self):
        rec = _export_tsv_gaps_record(MINIMAL)
        assert rec["has_duplicates"] is False

    def test_minimal_empty_column_count_zero(self):
        rec = _export_tsv_gaps_record(MINIMAL)
        assert rec["empty_column_count"] == 0

    def test_minimal_longest_row_index_zero(self):
        rec = _export_tsv_gaps_record(MINIMAL)
        assert rec["longest_row_index"] == 0

    def test_minimal_max_row_cell_count_is_two(self):
        rec = _export_tsv_gaps_record(MINIMAL)
        assert rec["max_row_cell_count"] == 2

    def test_minimal_distinct_value_ratio_is_one(self):
        rec = _export_tsv_gaps_record(MINIMAL)
        assert abs(rec["distinct_value_ratio"] - 1.0) < 0.01

    def test_minimal_field_length_sum_is_twelve(self):
        rec = _export_tsv_gaps_record(MINIMAL)
        assert rec["field_length_sum"] == 12

    def test_minimal_cell_to_row_ratio_is_two(self):
        rec = _export_tsv_gaps_record(MINIMAL)
        assert abs(rec["cell_to_row_ratio"] - 2.0) < 0.01

    def test_multi_max_row_cell_count_is_four(self):
        rec = _export_tsv_gaps_record(MULTI)
        assert rec["max_row_cell_count"] == 4

    def test_multi_cell_to_row_ratio_is_four(self):
        rec = _export_tsv_gaps_record(MULTI)
        assert abs(rec["cell_to_row_ratio"] - 4.0) < 0.01

    def test_record_has_all_keys(self):
        rec = _export_tsv_gaps_record(MINIMAL)
        for key in ["file", "has_duplicates", "empty_column_count",
                    "longest_row_index", "max_row_cell_count",
                    "distinct_value_ratio", "column_value_variance",
                    "field_length_sum", "cell_to_row_ratio"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_tsv_gaps_record(MINIMAL), _export_tsv_gaps_record(MULTI)]
        out = tmp_path / "tsv_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "field_length_sum" in parsed

    def test_ndjson_file_key_correct(self, tmp_path):
        records = [_export_tsv_gaps_record(MINIMAL)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "minimal-2x2.tsv"
