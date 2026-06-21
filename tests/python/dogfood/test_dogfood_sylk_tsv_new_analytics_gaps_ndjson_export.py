"""test_dogfood_sylk_tsv_new_analytics_gaps_ndjson_export.py

Dogfood export path: SYLK + TSV new analytics gap functions -> NDJSON.

Covers SYLK: sylk_total_cells, sylk_nonempty_cell_ratio, sylk_min_row_index,
sylk_max_row_index, sylk_numeric_cell_ratio.

Covers TSV: tsv_string_cell_count, tsv_total_string_length, tsv_nonempty_row_count,
tsv_avg_fields_per_row, tsv_nonempty_cell_ratio.

Concrete SYLK values (minimal-2x2.slk):
  total_cells         = 4
  nonempty_cell_ratio = 1.0
  min_row_index       = 1
  max_row_index       = 2
  numeric_cell_ratio  = 0.25

Concrete TSV values (minimal-2x2.tsv):
  string_cell_count  = 2
  total_string_length= 12
  nonempty_row_count = 2
  avg_fields_per_row = 2.0
  nonempty_cell_ratio= 1.0

Sprint: product-deepening-pgm-sylk-tsv-new-analytics-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import (
    sylk_total_cells,
    sylk_nonempty_cell_ratio,
    sylk_min_row_index,
    sylk_max_row_index,
    sylk_numeric_cell_ratio,
)
from src.python.tsv.tsv_parser import (
    tsv_string_cell_count,
    tsv_total_string_length,
    tsv_nonempty_row_count,
    tsv_avg_fields_per_row,
    tsv_nonempty_cell_ratio,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
TSV_DIR = _REPO / "samples" / "by-format" / "tsv"

SYLK_MINIMAL = SYLK_DIR / "minimal-2x2.slk"
SYLK_NUMERIC = SYLK_DIR / "numeric-row.slk"
TSV_MINIMAL = TSV_DIR / "minimal-2x2.tsv"
TSV_MULTI = TSV_DIR / "multi-column.tsv"


def _export_sylk_new_record(path: Path) -> dict:
    return {
        "file": path.name,
        "total_cells": sylk_total_cells(path),
        "nonempty_cell_ratio": sylk_nonempty_cell_ratio(path),
        "min_row_index": sylk_min_row_index(path),
        "max_row_index": sylk_max_row_index(path),
        "numeric_cell_ratio": sylk_numeric_cell_ratio(path),
    }


def _export_tsv_new_record(path: Path) -> dict:
    return {
        "file": path.name,
        "string_cell_count": tsv_string_cell_count(path),
        "total_string_length": tsv_total_string_length(path),
        "nonempty_row_count": tsv_nonempty_row_count(path),
        "avg_fields_per_row": tsv_avg_fields_per_row(path),
        "nonempty_cell_ratio": tsv_nonempty_cell_ratio(path),
    }


class TestSylkTsvNewAnalyticsGapsNdjsonExport:

    def test_sylk_minimal_total_cells(self):
        rec = _export_sylk_new_record(SYLK_MINIMAL)
        assert rec["total_cells"] == 4

    def test_sylk_minimal_nonempty_ratio_one(self):
        rec = _export_sylk_new_record(SYLK_MINIMAL)
        assert abs(rec["nonempty_cell_ratio"] - 1.0) < 0.001

    def test_sylk_minimal_min_row_index(self):
        rec = _export_sylk_new_record(SYLK_MINIMAL)
        assert rec["min_row_index"] == 1

    def test_sylk_minimal_max_row_index(self):
        rec = _export_sylk_new_record(SYLK_MINIMAL)
        assert rec["max_row_index"] == 2

    def test_sylk_minimal_numeric_cell_ratio(self):
        rec = _export_sylk_new_record(SYLK_MINIMAL)
        assert abs(rec["numeric_cell_ratio"] - 0.25) < 0.01

    def test_sylk_numeric_numeric_cell_ratio_one(self):
        rec = _export_sylk_new_record(SYLK_NUMERIC)
        assert abs(rec["numeric_cell_ratio"] - 1.0) < 0.01

    def test_tsv_minimal_string_cell_count(self):
        rec = _export_tsv_new_record(TSV_MINIMAL)
        assert rec["string_cell_count"] == 2

    def test_tsv_minimal_total_string_length(self):
        rec = _export_tsv_new_record(TSV_MINIMAL)
        assert rec["total_string_length"] == 12

    def test_tsv_minimal_nonempty_row_count(self):
        rec = _export_tsv_new_record(TSV_MINIMAL)
        assert rec["nonempty_row_count"] == 2

    def test_tsv_minimal_avg_fields_per_row(self):
        rec = _export_tsv_new_record(TSV_MINIMAL)
        assert abs(rec["avg_fields_per_row"] - 2.0) < 0.01

    def test_tsv_multi_string_cell_count(self):
        rec = _export_tsv_new_record(TSV_MULTI)
        assert rec["string_cell_count"] == 4

    def test_ndjson_export_sylk_and_tsv(self, tmp_path):
        records = [_export_sylk_new_record(SYLK_MINIMAL), _export_tsv_new_record(TSV_MINIMAL)]
        out = tmp_path / "sylk_tsv_new_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
