"""test_dogfood_dif_fodg_remaining_gaps_ndjson_export.py

Dogfood export path: DIF + FODG remaining analytics gap functions -> NDJSON.

Covers DIF: dif_row_width_variance, dif_distinct_numeric_count, dif_file_size_bytes,
            dif_unique_string_count, dif_max_row_cell_count, dif_min_row_cell_count,
            dif_has_mixed_types, dif_nonempty_cell_count, dif_max_row_width, dif_empty_cell_ratio
Covers FODG: fodg_text_density, fodg_page_text_variance, fodg_total_text_chars,
             fodg_min_text_per_page, fodg_nonempty_shape_ratio, fodg_shapes_with_text_count,
             fodg_nonempty_page_ratio, fodg_total_shapes_and_pages, fodg_all_pages_have_text,
             fodg_max_text_item_length

Concrete values:
  DIF minimal-2x2: row_width_var=0.0, distinct_numeric=2, file_size=187, unique_str=1,
                   max_row=8, min_row=8, mixed_types=True, nonempty_cells=8, max_width=8, empty_ratio=0.0
  DIF numeric-row: distinct_numeric=3, unique_str=0, max_row=3, mixed_types=False, nonempty=3
  DIF single-cell: distinct_numeric=1, max_row=1, nonempty=1
  FODG empty-page: text_density=0.0, total_text_chars=0, nonempty_page_ratio=0.0,
                   shapes_with_text=0, total_shapes_and_pages=1, all_pages_have_text=False
  FODG minimal-drawing: nonempty_page_ratio=1.0, total_shapes_and_pages=2, all_pages_have_text=True,
                        max_text_item_length=9
  FODG shapes-basic: total_shapes_and_pages=4, all_pages_have_text=True, max_text_item_length=7

Sprint: product-deepening-dif-fodg-remaining-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import (
    dif_row_width_variance,
    dif_distinct_numeric_count,
    dif_file_size_bytes,
    dif_unique_string_count,
    dif_max_row_cell_count,
    dif_min_row_cell_count,
    dif_has_mixed_types,
    dif_nonempty_cell_count,
    dif_max_row_width,
    dif_empty_cell_ratio,
)
from src.python.fodg.fodg_codec import (
    fodg_text_density,
    fodg_page_text_variance,
    fodg_total_text_chars,
    fodg_min_text_per_page,
    fodg_nonempty_shape_ratio,
    fodg_shapes_with_text_count,
    fodg_nonempty_page_ratio,
    fodg_total_shapes_and_pages,
    fodg_all_pages_have_text,
    fodg_max_text_item_length,
)
from src.python.ndjson.ndjson_codec import write_ndjson

DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
FODG_DIR = _REPO / "samples" / "by-format" / "fodg"

DIF_MINIMAL = DIF_DIR / "minimal-2x2.dif"
DIF_NUMERIC = DIF_DIR / "numeric-row.dif"
DIF_SINGLE = DIF_DIR / "single-cell.dif"
FODG_EMPTY = FODG_DIR / "empty-page.fodg"
FODG_MINIMAL = FODG_DIR / "minimal-drawing.fodg"
FODG_SHAPES = FODG_DIR / "shapes-basic.fodg"


class TestDifFodgRemainingGapsNdjsonExport:

    # DIF tests
    def test_dif_minimal_row_width_variance_zero(self):
        assert abs(dif_row_width_variance(DIF_MINIMAL)) < 0.01

    def test_dif_minimal_distinct_numeric_count(self):
        assert dif_distinct_numeric_count(DIF_MINIMAL) == 2

    def test_dif_numeric_distinct_numeric_count(self):
        assert dif_distinct_numeric_count(DIF_NUMERIC) == 3

    def test_dif_minimal_file_size_bytes(self):
        assert dif_file_size_bytes(DIF_MINIMAL) == 187

    def test_dif_minimal_unique_string_count(self):
        assert dif_unique_string_count(DIF_MINIMAL) == 1

    def test_dif_numeric_unique_string_count_zero(self):
        assert dif_unique_string_count(DIF_NUMERIC) == 0

    def test_dif_minimal_max_row_cell_count(self):
        assert dif_max_row_cell_count(DIF_MINIMAL) == 8

    def test_dif_minimal_min_row_cell_count(self):
        assert dif_min_row_cell_count(DIF_MINIMAL) == 8

    def test_dif_numeric_max_row_cell_count(self):
        assert dif_max_row_cell_count(DIF_NUMERIC) == 3

    def test_dif_minimal_has_mixed_types(self):
        assert dif_has_mixed_types(DIF_MINIMAL) is True

    def test_dif_numeric_not_mixed_types(self):
        assert dif_has_mixed_types(DIF_NUMERIC) is False

    def test_dif_minimal_nonempty_cell_count(self):
        assert dif_nonempty_cell_count(DIF_MINIMAL) == 8

    def test_dif_single_nonempty_cell_count(self):
        assert dif_nonempty_cell_count(DIF_SINGLE) == 1

    def test_dif_minimal_max_row_width(self):
        assert dif_max_row_width(DIF_MINIMAL) == 8

    def test_dif_numeric_max_row_width(self):
        assert dif_max_row_width(DIF_NUMERIC) == 3

    def test_dif_minimal_empty_cell_ratio_zero(self):
        assert abs(dif_empty_cell_ratio(DIF_MINIMAL)) < 0.01

    # FODG tests
    def test_fodg_empty_text_density_zero(self):
        assert abs(fodg_text_density(FODG_EMPTY)) < 0.01

    def test_fodg_empty_total_text_chars_zero(self):
        assert fodg_total_text_chars(FODG_EMPTY) == 0

    def test_fodg_empty_page_text_variance_zero(self):
        assert abs(fodg_page_text_variance(FODG_EMPTY)) < 0.01

    def test_fodg_empty_min_text_per_page_zero(self):
        assert fodg_min_text_per_page(FODG_EMPTY) == 0

    def test_fodg_empty_nonempty_shape_ratio_zero(self):
        assert abs(fodg_nonempty_shape_ratio(FODG_EMPTY)) < 0.01

    def test_fodg_empty_shapes_with_text_zero(self):
        assert fodg_shapes_with_text_count(FODG_EMPTY) == 0

    def test_fodg_empty_nonempty_page_ratio_zero(self):
        assert abs(fodg_nonempty_page_ratio(FODG_EMPTY)) < 0.01

    def test_fodg_empty_total_shapes_and_pages(self):
        assert fodg_total_shapes_and_pages(FODG_EMPTY) == 1

    def test_fodg_empty_not_all_pages_have_text(self):
        assert fodg_all_pages_have_text(FODG_EMPTY) is False

    def test_fodg_minimal_nonempty_page_ratio_one(self):
        assert abs(fodg_nonempty_page_ratio(FODG_MINIMAL) - 1.0) < 0.01

    def test_fodg_minimal_all_pages_have_text(self):
        assert fodg_all_pages_have_text(FODG_MINIMAL) is True

    def test_fodg_minimal_total_shapes_and_pages(self):
        assert fodg_total_shapes_and_pages(FODG_MINIMAL) == 2

    def test_fodg_minimal_max_text_item_length(self):
        assert fodg_max_text_item_length(FODG_MINIMAL) == 9

    def test_fodg_shapes_total_shapes_and_pages(self):
        assert fodg_total_shapes_and_pages(FODG_SHAPES) == 4

    def test_fodg_shapes_max_text_item_length(self):
        assert fodg_max_text_item_length(FODG_SHAPES) == 7

    # NDJSON export pipeline
    def test_ndjson_export_dif_fodg_records(self, tmp_path):
        records = [
            {
                "file": DIF_MINIMAL.name,
                "distinct_numeric_count": dif_distinct_numeric_count(DIF_MINIMAL),
                "has_mixed_types": dif_has_mixed_types(DIF_MINIMAL),
            },
            {
                "file": FODG_EMPTY.name,
                "total_text_chars": fodg_total_text_chars(FODG_EMPTY),
                "all_pages_have_text": fodg_all_pages_have_text(FODG_EMPTY),
            },
        ]
        out = tmp_path / "dif_fodg_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["has_mixed_types"] is True
        assert json.loads(lines[1])["total_text_chars"] == 0
