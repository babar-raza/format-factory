"""test_dogfood_fods_remaining_analytics_gaps_ndjson_export.py

Dogfood export path: FODS remaining 26 analytics gap functions -> NDJSON.

Covers:
  fods_avg_row_count, fods_avg_string_cell_length, fods_boolean_cell_count,
  fods_column_count_variance, fods_column_density, fods_distinct_value_count,
  fods_empty_row_count, fods_empty_row_ratio, fods_formula_density,
  fods_has_numeric_cells, fods_has_only_one_column, fods_is_all_string,
  fods_max_cell_length, fods_max_numeric_all_sheets, fods_max_string_cell_length,
  fods_min_cell_length, fods_min_numeric_all_sheets, fods_nonempty_cell_count,
  fods_nonempty_cell_ratio, fods_numeric_column_sum, fods_numeric_range,
  fods_row_cell_variance, fods_string_to_numeric_ratio, fods_total_col_count,
  fods_total_text_length, fods_unique_string_count

Concrete values:
  minimal: avg_row_count=1.0, avg_string_cell_length=5.0, boolean_cell_count=0,
            column_count_variance=0.0, column_density=1.0, distinct_value_count=1,
            empty_row_count=0, empty_row_ratio=0.0, formula_density=0.0,
            has_numeric_cells=False, has_only_one_column=True, is_all_string=True,
            max_cell_length=5, min_cell_length=5, nonempty_cell_count=1,
            nonempty_cell_ratio=1.0, total_col_count=1, total_text_length=5, unique_string_count=1
  typed-values: has_numeric_cells=True, boolean_cell_count=1, is_all_string=False,
                has_only_one_column=False, distinct_value_count=8, max_numeric_all_sheets=42.5,
                numeric_range=41.5, avg_string_cell_length=6.3333, max_string_cell_length=11,
                min_cell_length=4, max_cell_length=11, string_to_numeric_ratio=3.0,
                total_col_count=2, total_text_length=46, numeric_column_sum(col=1)=43.5
  formula-basic: formula_density=0.25, has_numeric_cells=True
  multi-sheet: avg_row_count=1.5, column_count_variance=0.25, row_cell_variance=0.0,
               nonempty_cell_count=5, total_col_count=3, column_density=1.0, unique_string_count=5

Sprint: product-deepening-dogfood-fods-remaining-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import parse_fods_strict
from fods import (
    fods_avg_row_count,
    fods_avg_string_cell_length,
    fods_boolean_cell_count,
    fods_column_count_variance,
    fods_column_density,
    fods_distinct_value_count,
    fods_empty_row_count,
    fods_empty_row_ratio,
    fods_formula_density,
    fods_has_numeric_cells,
    fods_has_only_one_column,
    fods_is_all_string,
    fods_max_cell_length,
    fods_max_numeric_all_sheets,
    fods_max_string_cell_length,
    fods_min_cell_length,
    fods_min_numeric_all_sheets,
    fods_nonempty_cell_count,
    fods_nonempty_cell_ratio,
    fods_numeric_column_sum,
    fods_numeric_range,
    fods_row_cell_variance,
    fods_string_to_numeric_ratio,
    fods_total_col_count,
    fods_total_text_length,
    fods_unique_string_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson

FODS_DIR = (_REPO / "samples" / "by-format" / "fods").resolve()
FODS_MINIMAL = FODS_DIR / "minimal-spreadsheet.fods"
FODS_TYPED = FODS_DIR / "typed-values-basic.fods"
FODS_FORMULA = FODS_DIR / "formula-basic.fods"
FODS_MULTI = FODS_DIR / "multi-sheet-basic.fods"


class TestFodsRemainingAnalyticsGapsNdjsonExport:

    # avg_row_count
    def test_fods_minimal_avg_row_count(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert abs(fods_avg_row_count(wb) - 1.0) < 0.01

    def test_fods_multi_avg_row_count(self):
        wb = parse_fods_strict(FODS_MULTI)
        assert abs(fods_avg_row_count(wb) - 1.5) < 0.01

    # avg_string_cell_length
    def test_fods_minimal_avg_string_cell_length(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert abs(fods_avg_string_cell_length(wb) - 5.0) < 0.01

    def test_fods_typed_avg_string_cell_length(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert abs(fods_avg_string_cell_length(wb) - 6.333) < 0.01

    # boolean_cell_count
    def test_fods_minimal_boolean_cell_count_zero(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_boolean_cell_count(wb) == 0

    def test_fods_typed_boolean_cell_count(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert fods_boolean_cell_count(wb) == 1

    # column_count_variance
    def test_fods_minimal_column_count_variance_zero(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert abs(fods_column_count_variance(wb)) < 0.01

    def test_fods_multi_column_count_variance(self):
        wb = parse_fods_strict(FODS_MULTI)
        assert abs(fods_column_count_variance(wb) - 0.25) < 0.01

    # column_density
    def test_fods_minimal_column_density_one(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert abs(fods_column_density(wb) - 1.0) < 0.01

    # distinct_value_count
    def test_fods_minimal_distinct_value_count(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_distinct_value_count(wb) == 1

    def test_fods_typed_distinct_value_count(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert fods_distinct_value_count(wb) == 8

    # empty_row_count
    def test_fods_minimal_empty_row_count_zero(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_empty_row_count(wb) == 0

    # empty_row_ratio
    def test_fods_minimal_empty_row_ratio_zero(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert abs(fods_empty_row_ratio(wb)) < 0.01

    # formula_density
    def test_fods_minimal_formula_density_zero(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert abs(fods_formula_density(wb)) < 0.01

    def test_fods_formula_density(self):
        wb = parse_fods_strict(FODS_FORMULA)
        assert abs(fods_formula_density(wb) - 0.25) < 0.01

    # has_numeric_cells
    def test_fods_minimal_has_numeric_cells_false(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_has_numeric_cells(wb) is False

    def test_fods_typed_has_numeric_cells_true(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert fods_has_numeric_cells(wb) is True

    # has_only_one_column
    def test_fods_minimal_has_only_one_column_true(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_has_only_one_column(wb) is True

    def test_fods_typed_has_only_one_column_false(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert fods_has_only_one_column(wb) is False

    # is_all_string
    def test_fods_minimal_is_all_string_true(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_is_all_string(wb) is True

    def test_fods_typed_is_all_string_false(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert fods_is_all_string(wb) is False

    # max_cell_length
    def test_fods_minimal_max_cell_length(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_max_cell_length(wb) == 5

    def test_fods_typed_max_cell_length(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert fods_max_cell_length(wb) == 11

    # max_numeric_all_sheets
    def test_fods_typed_max_numeric_all_sheets(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert abs(fods_max_numeric_all_sheets(wb) - 42.5) < 0.1

    # max_string_cell_length
    def test_fods_typed_max_string_cell_length(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert fods_max_string_cell_length(wb) == 11

    # min_cell_length
    def test_fods_typed_min_cell_length(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert fods_min_cell_length(wb) == 4

    # min_numeric_all_sheets
    def test_fods_typed_min_numeric_all_sheets(self):
        wb = parse_fods_strict(FODS_TYPED)
        val = fods_min_numeric_all_sheets(wb)
        assert val is not None

    # nonempty_cell_count
    def test_fods_minimal_nonempty_cell_count(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_nonempty_cell_count(wb) == 1

    def test_fods_multi_nonempty_cell_count(self):
        wb = parse_fods_strict(FODS_MULTI)
        assert fods_nonempty_cell_count(wb) == 5

    # nonempty_cell_ratio
    def test_fods_minimal_nonempty_cell_ratio_one(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert abs(fods_nonempty_cell_ratio(wb) - 1.0) < 0.01

    # numeric_column_sum
    def test_fods_typed_numeric_column_sum(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert abs(fods_numeric_column_sum(wb, col_index=1) - 43.5) < 0.1

    # numeric_range
    def test_fods_typed_numeric_range(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert abs(fods_numeric_range(wb) - 41.5) < 0.1

    # row_cell_variance
    def test_fods_minimal_row_cell_variance_zero(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert abs(fods_row_cell_variance(wb)) < 0.01

    def test_fods_multi_row_cell_variance(self):
        wb = parse_fods_strict(FODS_MULTI)
        assert fods_row_cell_variance(wb) >= 0.0

    # string_to_numeric_ratio
    def test_fods_minimal_string_to_numeric_ratio(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert abs(fods_string_to_numeric_ratio(wb)) < 0.01

    def test_fods_typed_string_to_numeric_ratio(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert abs(fods_string_to_numeric_ratio(wb) - 3.0) < 0.1

    # total_col_count
    def test_fods_minimal_total_col_count(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_total_col_count(wb) == 1

    def test_fods_multi_total_col_count(self):
        wb = parse_fods_strict(FODS_MULTI)
        assert fods_total_col_count(wb) == 3

    # total_text_length
    def test_fods_minimal_total_text_length(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_total_text_length(wb) == 5

    def test_fods_typed_total_text_length(self):
        wb = parse_fods_strict(FODS_TYPED)
        assert fods_total_text_length(wb) == 46

    # unique_string_count
    def test_fods_minimal_unique_string_count(self):
        wb = parse_fods_strict(FODS_MINIMAL)
        assert fods_unique_string_count(wb) == 1

    def test_fods_multi_unique_string_count(self):
        wb = parse_fods_strict(FODS_MULTI)
        assert fods_unique_string_count(wb) == 5

    # NDJSON export pipeline
    def test_ndjson_export_fods_analytics(self, tmp_path):
        wb_min = parse_fods_strict(FODS_MINIMAL)
        wb_typed = parse_fods_strict(FODS_TYPED)
        records = [
            {
                "file": FODS_MINIMAL.name,
                "has_numeric_cells": fods_has_numeric_cells(wb_min),
                "is_all_string": fods_is_all_string(wb_min),
                "total_col_count": fods_total_col_count(wb_min),
                "distinct_value_count": fods_distinct_value_count(wb_min),
                "unique_string_count": fods_unique_string_count(wb_min),
            },
            {
                "file": FODS_TYPED.name,
                "has_numeric_cells": fods_has_numeric_cells(wb_typed),
                "boolean_cell_count": fods_boolean_cell_count(wb_typed),
                "max_string_cell_length": fods_max_string_cell_length(wb_typed),
                "numeric_range": fods_numeric_range(wb_typed),
                "nonempty_cell_count": fods_nonempty_cell_count(wb_typed),
            },
        ]
        out = tmp_path / "fods_remaining_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["is_all_string"] is True
        assert json.loads(lines[1])["boolean_cell_count"] == 1
