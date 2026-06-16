"""test_dogfood_csv_analytics_gaps_ndjson_export.py

Dogfood export path: CSV statistics analytics gaps → NDJSON.

Covers gap functions: csv_avg_cell_length, csv_avg_numeric_value,
csv_empty_column_count, csv_longest_row_index, csv_total_string_length,
csv_is_square, csv_column_value_variance, csv_header_length_sum.

Concrete values (minimal-2x2.csv):
  avg_cell_length     = 3.0
  avg_numeric_value   = 27.5
  empty_column_count  = 0
  longest_row_index   = 0
  total_string_length = 12
  is_square           = True
  header_length_sum   = 7

Sprint: product-deepening-csv-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_avg_cell_length,
    csv_avg_numeric_value,
    csv_empty_column_count,
    csv_longest_row_index,
    csv_total_string_length,
    csv_is_square,
    csv_column_value_variance,
    csv_header_length_sum,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "csv"
MINIMAL = SAMPLES_DIR / "minimal-2x2.csv"
QUOTED = SAMPLES_DIR / "quoted-fields.csv"


def _export_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "avg_cell_length": csv_avg_cell_length(path),
        "avg_numeric_value": csv_avg_numeric_value(path),
        "empty_column_count": csv_empty_column_count(path),
        "longest_row_index": csv_longest_row_index(path),
        "total_string_length": csv_total_string_length(path),
        "is_square": csv_is_square(path),
        "column_value_variance": csv_column_value_variance(path),
        "header_length_sum": csv_header_length_sum(path),
    }


class TestCsvAnalyticsGapsNdjsonExport:

    def test_minimal_avg_cell_length_is_three(self):
        rec = _export_gaps_record(MINIMAL)
        assert abs(rec["avg_cell_length"] - 3.0) < 0.01

    def test_minimal_avg_numeric_value_is_27_5(self):
        rec = _export_gaps_record(MINIMAL)
        assert abs(rec["avg_numeric_value"] - 27.5) < 0.01

    def test_minimal_empty_column_count_zero(self):
        rec = _export_gaps_record(MINIMAL)
        assert rec["empty_column_count"] == 0

    def test_minimal_longest_row_index_zero(self):
        rec = _export_gaps_record(MINIMAL)
        assert rec["longest_row_index"] == 0

    def test_minimal_total_string_length_twelve(self):
        rec = _export_gaps_record(MINIMAL)
        assert rec["total_string_length"] == 12

    def test_minimal_is_square(self):
        rec = _export_gaps_record(MINIMAL)
        assert rec["is_square"] is True

    def test_minimal_header_length_sum_seven(self):
        rec = _export_gaps_record(MINIMAL)
        assert rec["header_length_sum"] == 7

    def test_quoted_not_square(self):
        rec = _export_gaps_record(QUOTED)
        assert rec["is_square"] is False

    def test_record_has_all_keys(self):
        rec = _export_gaps_record(MINIMAL)
        for key in ["file", "avg_cell_length", "avg_numeric_value",
                    "empty_column_count", "longest_row_index",
                    "total_string_length", "is_square",
                    "column_value_variance", "header_length_sum"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_gaps_record(MINIMAL), _export_gaps_record(QUOTED)]
        out = tmp_path / "csv_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "total_string_length" in parsed

    def test_ndjson_file_key_correct(self, tmp_path):
        records = [_export_gaps_record(MINIMAL)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "minimal-2x2.csv"

    def test_variance_non_negative(self):
        rec = _export_gaps_record(MINIMAL)
        assert rec["column_value_variance"] >= 0.0
