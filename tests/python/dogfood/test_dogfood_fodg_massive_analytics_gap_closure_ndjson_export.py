"""
tests/python/dogfood/test_dogfood_fodg_massive_analytics_gap_closure_ndjson_export.py

Sprint: dogfood-fodg-analytics-gap-closure-20260617
Dogfood export: FODG analytics -> NDJSON roundtrip.
Covers 51 previously-untested fodg_* analytics functions.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    load as fodg_load,
    fodg_all_pages_have_shapes,
    fodg_all_pages_have_text,
    fodg_avg_shapes_per_nonempty_page,
    fodg_avg_shapes_per_page,
    fodg_avg_text_item_length,
    fodg_avg_text_per_page,
    fodg_avg_text_per_shape,
    fodg_empty_page_count,
    fodg_file_size_bytes,
    fodg_has_empty_pages,
    fodg_has_multiple_pages,
    fodg_has_multiple_shapes,
    fodg_has_no_shapes,
    fodg_has_non_text_shapes,
    fodg_has_single_shape,
    fodg_has_text,
    fodg_is_empty_document,
    fodg_is_empty_drawing,
    fodg_is_single_page,
    fodg_max_shape_text_length,
    fodg_max_shapes_per_page,
    fodg_max_text_item_length,
    fodg_min_shape_count,
    fodg_min_shapes_per_page,
    fodg_min_text_item_length,
    fodg_min_text_per_page,
    fodg_non_text_shape_count,
    fodg_nonempty_page_count,
    fodg_nonempty_page_ratio,
    fodg_nonempty_shape_ratio,
    fodg_page_count,
    fodg_page_shape_count,
    fodg_page_text_variance,
    fodg_shape_density,
    fodg_shape_text_ratio,
    fodg_shapes_exceed_pages,
    fodg_shapes_with_text_count,
    fodg_text_and_shape_sum,
    fodg_text_density,
    fodg_text_item_count,
    fodg_text_item_length_range,
    fodg_text_items_exceed_pages,
    fodg_text_items_per_shape,
    fodg_text_per_shape,
    fodg_text_shape_count,
    fodg_text_to_shape_ratio,
    fodg_total_shape_count,
    fodg_total_shapes_and_pages,
    fodg_total_text_chars,
    fodg_unique_text_item_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
_SHAPES = str(_FODG_DIR / "shapes-basic.fodg")
_EMPTY = str(_FODG_DIR / "empty-page.fodg")


class TestFodgMassiveAnalyticsGapClosureNdjsonExport:
    """51 FODG analytics functions -> NDJSON dogfood export."""

    # --- boolean analytics on shapes-basic.fodg ---

    def test_all_pages_have_shapes(self):
        assert fodg_all_pages_have_shapes(_SHAPES) is True

    def test_all_pages_have_text(self):
        assert fodg_all_pages_have_text(_SHAPES) is True

    def test_has_empty_pages_false(self):
        assert fodg_has_empty_pages(_SHAPES) is False

    def test_has_multiple_pages_false(self):
        assert fodg_has_multiple_pages(_SHAPES) is False

    def test_has_multiple_shapes_true(self):
        assert fodg_has_multiple_shapes(_SHAPES) is True

    def test_has_no_shapes_false(self):
        assert fodg_has_no_shapes(_SHAPES) is False

    def test_has_non_text_shapes_true(self):
        assert fodg_has_non_text_shapes(_SHAPES) is True

    def test_has_single_shape_false(self):
        assert fodg_has_single_shape(_SHAPES) is False

    def test_has_text_false(self):
        # shapes-basic has text items but total_text_chars == 0
        assert fodg_has_text(_SHAPES) is False

    def test_is_empty_document_false(self):
        assert fodg_is_empty_document(_SHAPES) is False

    def test_is_empty_drawing_false(self):
        assert fodg_is_empty_drawing(_SHAPES) is False

    def test_is_single_page_true(self):
        assert fodg_is_single_page(_SHAPES) is True

    def test_shapes_exceed_pages_true(self):
        assert fodg_shapes_exceed_pages(_SHAPES) is True

    def test_text_items_exceed_pages_true(self):
        assert fodg_text_items_exceed_pages(_SHAPES) is True

    # --- numeric analytics on shapes-basic.fodg ---

    def test_avg_shapes_per_nonempty_page(self):
        assert fodg_avg_shapes_per_nonempty_page(_SHAPES) == 3.0

    def test_avg_shapes_per_page(self):
        assert fodg_avg_shapes_per_page(_SHAPES) == 3.0

    def test_avg_text_item_length(self):
        assert fodg_avg_text_item_length(_SHAPES) == 5.5

    def test_avg_text_per_page(self):
        assert fodg_avg_text_per_page(_SHAPES) == 0.0

    def test_avg_text_per_shape(self):
        assert fodg_avg_text_per_shape(_SHAPES) == 0.0

    def test_empty_page_count(self):
        assert fodg_empty_page_count(_SHAPES) == 0

    def test_file_size_bytes(self):
        val = fodg_file_size_bytes(_SHAPES)
        assert isinstance(val, int)
        assert val > 0

    def test_max_shape_text_length(self):
        assert fodg_max_shape_text_length(_SHAPES) == 0

    def test_max_shapes_per_page(self):
        assert fodg_max_shapes_per_page(_SHAPES) == 3

    def test_max_text_item_length(self):
        assert fodg_max_text_item_length(_SHAPES) == 7

    def test_min_shape_count(self):
        assert fodg_min_shape_count(_SHAPES) == 3

    def test_min_shapes_per_page(self):
        assert fodg_min_shapes_per_page(_SHAPES) == 3

    def test_min_text_item_length(self):
        assert fodg_min_text_item_length(_SHAPES) == 4

    def test_min_text_per_page(self):
        assert fodg_min_text_per_page(_SHAPES) == 0

    def test_non_text_shape_count(self):
        assert fodg_non_text_shape_count(_SHAPES) == 2

    def test_nonempty_page_count(self):
        assert fodg_nonempty_page_count(_SHAPES) == 1

    def test_nonempty_page_ratio(self):
        assert fodg_nonempty_page_ratio(_SHAPES) == 1.0

    def test_nonempty_shape_ratio(self):
        assert fodg_nonempty_shape_ratio(_SHAPES) == 0.0

    def test_page_count(self):
        assert fodg_page_count(_SHAPES) == 1

    def test_page_shape_count_model_based(self):
        doc = fodg_load(_SHAPES)
        assert fodg_page_shape_count(doc, 0) == 3

    def test_page_text_variance(self):
        assert fodg_page_text_variance(_SHAPES) == 0.0

    def test_shape_density(self):
        assert fodg_shape_density(_SHAPES) == 3.0

    def test_shape_text_ratio(self):
        assert fodg_shape_text_ratio(_SHAPES) == 0.0

    def test_shapes_with_text_count(self):
        assert fodg_shapes_with_text_count(_SHAPES) == 0

    def test_text_and_shape_sum(self):
        assert fodg_text_and_shape_sum(_SHAPES) == 5

    def test_text_density(self):
        assert fodg_text_density(_SHAPES) == 0.0

    def test_text_item_count(self):
        assert fodg_text_item_count(_SHAPES) == 2

    def test_text_item_length_range(self):
        assert fodg_text_item_length_range(_SHAPES) == 3

    def test_text_items_per_shape(self):
        val = fodg_text_items_per_shape(_SHAPES)
        assert abs(val - 0.6667) < 0.001

    def test_text_per_shape(self):
        assert fodg_text_per_shape(_SHAPES) == 0.0

    def test_text_shape_count(self):
        assert fodg_text_shape_count(_SHAPES) == 1

    def test_text_to_shape_ratio(self):
        val = fodg_text_to_shape_ratio(_SHAPES)
        assert val >= 0.0

    def test_total_shape_count(self):
        assert fodg_total_shape_count(_SHAPES) == 3

    def test_total_shapes_and_pages(self):
        assert fodg_total_shapes_and_pages(_SHAPES) == 4

    def test_total_text_chars(self):
        assert fodg_total_text_chars(_SHAPES) == 0

    def test_unique_text_item_count(self):
        assert fodg_unique_text_item_count(_SHAPES) == 2

    # --- empty-page.fodg tests ---

    def test_empty_page_is_empty_drawing(self):
        assert fodg_is_empty_drawing(_EMPTY) is True

    def test_empty_page_has_empty_pages(self):
        assert fodg_has_empty_pages(_EMPTY) is True

    def test_empty_page_empty_page_count(self):
        assert fodg_empty_page_count(_EMPTY) == 1

    # --- NDJSON roundtrip export ---

    def test_ndjson_roundtrip_analytics_export(self, tmp_path):
        out = tmp_path / "fodg_analytics.ndjson"
        records = [
            {"fn": "page_count", "value": fodg_page_count(_SHAPES)},
            {"fn": "total_shape_count", "value": fodg_total_shape_count(_SHAPES)},
            {"fn": "text_item_count", "value": fodg_text_item_count(_SHAPES)},
            {"fn": "file_size_bytes", "value": fodg_file_size_bytes(_SHAPES)},
            {"fn": "avg_shapes_per_page", "value": fodg_avg_shapes_per_page(_SHAPES)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 5
        assert loaded[0]["fn"] == "page_count"
        assert loaded[0]["value"] == 1
        assert loaded[1]["value"] == 3
        assert loaded[2]["value"] == 2
        assert loaded[4]["value"] == 3.0
