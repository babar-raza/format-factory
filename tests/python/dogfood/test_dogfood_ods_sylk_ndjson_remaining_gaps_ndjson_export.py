"""test_dogfood_ods_sylk_ndjson_remaining_gaps_ndjson_export.py

Dogfood export path: ODS + SYLK + NDJSON remaining analytics gap functions -> NDJSON.

Covers ODS: ods_avg_string_length, ods_empty_sheet_count, ods_merged_cell_ratio,
            ods_nonempty_cell_ratio, ods_total_numeric_cells
Covers SYLK: sylk_avg_cell_length_per_row, sylk_first_row_cell_count, sylk_has_empty_cells,
             sylk_max_cells_in_col, sylk_max_row_cell_count, sylk_max_value_count
Covers NDJSON: ndjson_avg_record_depth, ndjson_record_type_variance

Concrete values:
  ODS minimal-spreadsheet: avg_string_length=4.67, empty_sheet_count=0, nonempty_cell_ratio=1.0, total_numeric_cells=1
  ODS numeric-row: avg_string_length=0.0, total_numeric_cells=3
  ODS single-cell: avg_string_length=2.0, total_numeric_cells=0
  SYLK minimal-2x2: avg_cell_length_per_row=4.0, first_row_cell_count=2, has_empty_cells=False,
                    max_cells_in_col=2, max_row_cell_count=2, max_value_count=1
  SYLK numeric-row: first_row_cell_count=3, max_row_cell_count=3
  NDJSON nested: avg_record_depth=2.0, record_type_variance=0.0

Sprint: product-deepening-ods-sylk-ndjson-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import (
    ods_avg_string_length,
    ods_empty_sheet_count,
    ods_merged_cell_ratio,
    ods_nonempty_cell_ratio,
    ods_total_numeric_cells,
)
from src.python.sylk.sylk_parser import (
    sylk_avg_cell_length_per_row,
    sylk_first_row_cell_count,
    sylk_has_empty_cells,
    sylk_max_cells_in_col,
    sylk_max_row_cell_count,
    sylk_max_value_count,
)
from src.python.ndjson.ndjson_codec import (
    ndjson_avg_record_depth,
    ndjson_record_type_variance,
    write_ndjson,
)

ODS_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"

ODS_MINIMAL = ODS_DIR / "minimal-spreadsheet.ods"
ODS_NUMERIC = ODS_DIR / "numeric-row.ods"
ODS_SINGLE = ODS_DIR / "single-cell.ods"
SYLK_MINIMAL = SYLK_DIR / "minimal-2x2.slk"
SYLK_NUMERIC = SYLK_DIR / "numeric-row.slk"
SYLK_SINGLE = SYLK_DIR / "single-cell.slk"


class TestOdsSylkNdjsonRemainingGapsNdjsonExport:

    # ODS tests
    def test_ods_minimal_avg_string_length(self):
        assert abs(ods_avg_string_length(ODS_MINIMAL) - 4.67) < 0.1

    def test_ods_numeric_avg_string_length_zero(self):
        assert abs(ods_avg_string_length(ODS_NUMERIC)) < 0.01

    def test_ods_single_avg_string_length(self):
        assert abs(ods_avg_string_length(ODS_SINGLE) - 2.0) < 0.1

    def test_ods_minimal_empty_sheet_count_zero(self):
        assert ods_empty_sheet_count(ODS_MINIMAL) == 0

    def test_ods_minimal_merged_cell_ratio_zero(self):
        assert abs(ods_merged_cell_ratio(ODS_MINIMAL)) < 0.01

    def test_ods_minimal_nonempty_cell_ratio_one(self):
        assert abs(ods_nonempty_cell_ratio(ODS_MINIMAL) - 1.0) < 0.01

    def test_ods_minimal_total_numeric_cells(self):
        assert ods_total_numeric_cells(ODS_MINIMAL) == 1

    def test_ods_numeric_total_numeric_cells(self):
        assert ods_total_numeric_cells(ODS_NUMERIC) == 3

    def test_ods_single_total_numeric_cells_zero(self):
        assert ods_total_numeric_cells(ODS_SINGLE) == 0

    # SYLK tests
    def test_sylk_minimal_avg_cell_length_per_row(self):
        assert abs(sylk_avg_cell_length_per_row(SYLK_MINIMAL) - 4.0) < 0.1

    def test_sylk_numeric_avg_cell_length_per_row(self):
        assert abs(sylk_avg_cell_length_per_row(SYLK_NUMERIC) - 1.0) < 0.1

    def test_sylk_minimal_first_row_cell_count(self):
        assert sylk_first_row_cell_count(SYLK_MINIMAL) == 2

    def test_sylk_numeric_first_row_cell_count(self):
        assert sylk_first_row_cell_count(SYLK_NUMERIC) == 3

    def test_sylk_minimal_has_empty_cells_false(self):
        assert sylk_has_empty_cells(SYLK_MINIMAL) is False

    def test_sylk_minimal_max_cells_in_col(self):
        assert sylk_max_cells_in_col(SYLK_MINIMAL) == 2

    def test_sylk_single_max_cells_in_col(self):
        assert sylk_max_cells_in_col(SYLK_SINGLE) == 1

    def test_sylk_minimal_max_row_cell_count(self):
        assert sylk_max_row_cell_count(SYLK_MINIMAL) == 2

    def test_sylk_numeric_max_row_cell_count(self):
        assert sylk_max_row_cell_count(SYLK_NUMERIC) == 3

    def test_sylk_minimal_max_value_count(self):
        assert sylk_max_value_count(SYLK_MINIMAL) == 1

    # NDJSON tests (using tmp_path to create test files)
    def test_ndjson_avg_record_depth_flat(self, tmp_path):
        ndjson_file = tmp_path / "flat.ndjson"
        write_ndjson([{"a": 1, "b": 2}, {"a": 3, "b": 4}], str(ndjson_file))
        assert abs(ndjson_avg_record_depth(ndjson_file) - 1.0) < 0.01

    def test_ndjson_avg_record_depth_nested(self, tmp_path):
        ndjson_file = tmp_path / "nested.ndjson"
        ndjson_file.write_text(
            '{"a": 1, "b": {"x": 2}}\n{"a": 3, "b": {"x": 4}}\n',
            encoding="utf-8"
        )
        assert abs(ndjson_avg_record_depth(ndjson_file) - 2.0) < 0.01

    def test_ndjson_record_type_variance_uniform(self, tmp_path):
        ndjson_file = tmp_path / "uniform.ndjson"
        write_ndjson([{"a": 1}, {"a": 2}], str(ndjson_file))
        assert abs(ndjson_record_type_variance(ndjson_file)) < 0.01

    def test_ndjson_export_ods_record(self, tmp_path):
        records = [{
            "file": ODS_MINIMAL.name,
            "total_numeric_cells": ods_total_numeric_cells(ODS_MINIMAL),
            "nonempty_cell_ratio": ods_nonempty_cell_ratio(ODS_MINIMAL),
        }]
        out = tmp_path / "ods_remaining.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["total_numeric_cells"] == 1

    def test_ndjson_export_sylk_record(self, tmp_path):
        records = [
            {"file": SYLK_MINIMAL.name, "max_row_cell_count": sylk_max_row_cell_count(SYLK_MINIMAL)},
            {"file": SYLK_NUMERIC.name, "max_row_cell_count": sylk_max_row_cell_count(SYLK_NUMERIC)},
        ]
        out = tmp_path / "sylk_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["max_row_cell_count"] == 2
        assert json.loads(lines[1])["max_row_cell_count"] == 3
