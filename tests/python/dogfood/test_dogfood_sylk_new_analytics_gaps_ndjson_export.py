"""test_dogfood_sylk_new_analytics_gaps_ndjson_export.py

Dogfood export path: SYLK new analytics gap functions -> NDJSON.

Covers: sylk_avg_cell_length, sylk_avg_numeric_value, sylk_avg_row_density,
sylk_cell_count_variance, sylk_string_value_count.

Concrete values (minimal-2x2.slk):
  avg_cell_length     = 4.0
  avg_numeric_value   = 42.0
  avg_row_density     = 2.0
  cell_count_variance = 0.0
  string_value_count  = 3

Concrete values (numeric-row.slk):
  avg_cell_length     = 1.0
  avg_numeric_value   = 2.0
  string_value_count  = 0

Sprint: product-deepening-dif-sylk-new-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import (
    sylk_avg_cell_length,
    sylk_avg_numeric_value,
    sylk_avg_row_density,
    sylk_cell_count_variance,
    sylk_string_value_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
MINIMAL_2X2 = SAMPLES_DIR / "minimal-2x2.slk"
NUMERIC_ROW = SAMPLES_DIR / "numeric-row.slk"
SINGLE_CELL = SAMPLES_DIR / "single-cell.slk"


def _export_sylk_new_record(path: Path) -> dict:
    return {
        "file": path.name,
        "avg_cell_length": sylk_avg_cell_length(path),
        "avg_numeric_value": sylk_avg_numeric_value(path),
        "avg_row_density": sylk_avg_row_density(path),
        "cell_count_variance": sylk_cell_count_variance(path),
        "string_value_count": sylk_string_value_count(path),
    }


class TestSylkNewAnalyticsGapsNdjsonExport:

    def test_minimal_avg_cell_length(self):
        rec = _export_sylk_new_record(MINIMAL_2X2)
        assert abs(rec["avg_cell_length"] - 4.0) < 0.01

    def test_numeric_row_avg_cell_length_one(self):
        rec = _export_sylk_new_record(NUMERIC_ROW)
        assert abs(rec["avg_cell_length"] - 1.0) < 0.01

    def test_minimal_avg_numeric_value(self):
        rec = _export_sylk_new_record(MINIMAL_2X2)
        assert abs(rec["avg_numeric_value"] - 42.0) < 0.1

    def test_numeric_row_avg_numeric_value(self):
        rec = _export_sylk_new_record(NUMERIC_ROW)
        assert abs(rec["avg_numeric_value"] - 2.0) < 0.1

    def test_minimal_avg_row_density(self):
        rec = _export_sylk_new_record(MINIMAL_2X2)
        assert abs(rec["avg_row_density"] - 2.0) < 0.01

    def test_single_cell_avg_row_density_one(self):
        rec = _export_sylk_new_record(SINGLE_CELL)
        assert abs(rec["avg_row_density"] - 1.0) < 0.01

    def test_minimal_cell_count_variance_zero(self):
        rec = _export_sylk_new_record(MINIMAL_2X2)
        assert abs(rec["cell_count_variance"]) < 0.001

    def test_minimal_string_value_count_three(self):
        rec = _export_sylk_new_record(MINIMAL_2X2)
        assert rec["string_value_count"] == 3

    def test_numeric_row_string_value_count_zero(self):
        rec = _export_sylk_new_record(NUMERIC_ROW)
        assert rec["string_value_count"] == 0

    def test_record_has_all_keys(self):
        rec = _export_sylk_new_record(MINIMAL_2X2)
        for key in ["file", "avg_cell_length", "avg_numeric_value",
                    "avg_row_density", "cell_count_variance", "string_value_count"]:
            assert key in rec

    def test_ndjson_export_two_files(self, tmp_path):
        records = [_export_sylk_new_record(MINIMAL_2X2), _export_sylk_new_record(NUMERIC_ROW)]
        out = tmp_path / "sylk_new_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            parsed = json.loads(line)
            assert "avg_cell_length" in parsed

    def test_ndjson_file_key_correct(self, tmp_path):
        records = [_export_sylk_new_record(MINIMAL_2X2)]
        out = tmp_path / "single.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["file"] == "minimal-2x2.slk"
