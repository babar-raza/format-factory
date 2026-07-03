"""test_dogfood_sylk_analytics_gaps_ndjson_export.py

Dogfood export path: SYLK analytics gap functions → NDJSON.

Covers: sylk_is_all_numeric, sylk_row_span, sylk_is_square,
sylk_total_string_length, sylk_longest_row_index, sylk_string_value_count.

Concrete values (minimal-2x2.slk):
  is_all_numeric       = False
  row_span             = 2
  is_square            = True
  total_string_length  = 16
  longest_row_index    = 1
  string_value_count   = 3

Sprint: product-deepening-sylk-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_analytics import sylk_is_all_numeric, sylk_row_span, sylk_is_square, sylk_total_string_length, sylk_longest_row_index, sylk_string_value_count
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
MINIMAL = SAMPLES_DIR / "minimal-2x2.slk"
NUMERIC = SAMPLES_DIR / "numeric-row.slk"


def _export_sylk_gaps_record(path: Path) -> dict:
    return {
        "file": path.name,
        "is_all_numeric": sylk_is_all_numeric(path),
        "row_span": sylk_row_span(path),
        "is_square": sylk_is_square(path),
        "total_string_length": sylk_total_string_length(path),
        "longest_row_index": sylk_longest_row_index(path),
        "string_value_count": sylk_string_value_count(path),
    }


class TestSylkAnalyticsGapsNdjsonExport:

    def test_minimal_not_all_numeric(self):
        rec = _export_sylk_gaps_record(MINIMAL)
        assert rec["is_all_numeric"] is False

    def test_minimal_row_span_is_two(self):
        rec = _export_sylk_gaps_record(MINIMAL)
        assert rec["row_span"] == 2

    def test_minimal_is_square(self):
        rec = _export_sylk_gaps_record(MINIMAL)
        assert rec["is_square"] is True

    def test_minimal_total_string_length_is_sixteen(self):
        rec = _export_sylk_gaps_record(MINIMAL)
        assert rec["total_string_length"] == 16

    def test_minimal_longest_row_index_is_one(self):
        rec = _export_sylk_gaps_record(MINIMAL)
        assert rec["longest_row_index"] == 1

    def test_minimal_string_value_count_is_three(self):
        rec = _export_sylk_gaps_record(MINIMAL)
        assert rec["string_value_count"] == 3

    def test_numeric_is_all_numeric(self):
        rec = _export_sylk_gaps_record(NUMERIC)
        assert rec["is_all_numeric"] is True

    def test_numeric_not_square(self):
        rec = _export_sylk_gaps_record(NUMERIC)
        assert rec["is_square"] is False

    def test_record_has_all_keys(self):
        rec = _export_sylk_gaps_record(MINIMAL)
        for key in ["file", "is_all_numeric", "row_span", "is_square",
                    "total_string_length", "longest_row_index", "string_value_count"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_sylk_gaps_record(MINIMAL), _export_sylk_gaps_record(NUMERIC)]
        out = tmp_path / "sylk_gap_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "string_value_count" in parsed

    def test_ndjson_file_key_correct(self, tmp_path):
        records = [_export_sylk_gaps_record(MINIMAL)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "minimal-2x2.slk"

    def test_numeric_string_value_count_zero(self):
        rec = _export_sylk_gaps_record(NUMERIC)
        assert rec["string_value_count"] == 0
