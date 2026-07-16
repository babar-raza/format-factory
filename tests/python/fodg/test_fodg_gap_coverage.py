"""
Gap-coverage tests for src/python/fodg — comprehensive exercise of the FODG
public API surface (fodg_codec, drawing_document, drawing_metrics, models,
Compat facades, fodg_page_iterator, fodg_workflow, exceptions, cli).

This file closes missing_test_coverage gaps by exercising every function
reachable from the `fodg` package's public `__all__`, plus the internal
Compat/, spec/, exceptions.py, and cli.py modules that are not re-exported.

Expected values for the file-based analytics functions were captured by
directly invoking each function against the three canonical corpus samples
(minimal-drawing.fodg, shapes-basic.fodg, empty-page.fodg) and are asserted
verbatim below — this is snapshot-style regression coverage, not a
reimplementation of the functions under test.

Ground-truth note: the neutral model's per-page "shapes" list (as returned
by load()) is always empty — fodg_codec._extract_pages() never populates it;
only the module-level get_shapes(source) function parses shapes directly
from XML. Consequently several drawing_document.py / drawing_metrics.py
functions that iterate page["shapes"] (e.g. fodg_total_text_chars,
fodg_avg_text_per_shape, fodg_shapes_with_text_count, fodg_max_shape_text_length,
fodg_nonempty_shape_ratio, fodg_page_text_variance, fodg_shape_count_variance,
fodg_min_text_per_page) always evaluate against an empty shapes list for any
file loaded via load() and therefore return 0 / 0.0 for real corpus samples.
This is documented, real, current behavior — tests assert it as-is.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pytest

import fodg
from fodg import cli as fodg_cli
from fodg.models import FodgDocument
from fodg import exceptions as fodg_exceptions

REPO_ROOT = _REPO
SAMPLES_DIR = REPO_ROOT / "samples" / "by-format" / "fodg"

MINIMAL = SAMPLES_DIR / "minimal-drawing.fodg"
SHAPES_BASIC = SAMPLES_DIR / "shapes-basic.fodg"
EMPTY_PAGE = SAMPLES_DIR / "empty-page.fodg"

SAMPLE_MAP = {
    "minimal": MINIMAL,
    "shapes_basic": SHAPES_BASIC,
    "empty_page": EMPTY_PAGE,
}


# ---------------------------------------------------------------------------
# Section 1 — bulk snapshot coverage for all (source) -> value functions
# exported from the fodg package (fodg_codec + drawing_document +
# drawing_metrics). Each tuple is (function_name, sample_label, expected).
# ---------------------------------------------------------------------------

BULK_CASES = [
    ("export_to_csv", "minimal", 'page_name,shape_index,text\nPage1,0,Rectangle\n'),
    ("export_to_csv", "shapes_basic", 'page_name,shape_index,text\nPage1,0,Rect\nPage1,1,Ellipse\n'),
    ("export_to_csv", "empty_page", 'page_name,shape_index,text\n'),
    ("export_to_txt", "minimal", '=== Page1 ===\nRectangle'),
    ("export_to_txt", "shapes_basic", '=== Page1 ===\nRect\nEllipse'),
    ("export_to_txt", "empty_page", '=== Page1 ==='),
    ("extract_text", "minimal", ['Rectangle']),
    ("extract_text", "shapes_basic", ['Rect', 'Ellipse']),
    ("extract_text", "empty_page", []),
    ("fodg_all_pages_have_shapes", "minimal", True),
    ("fodg_all_pages_have_shapes", "shapes_basic", True),
    ("fodg_all_pages_have_shapes", "empty_page", False),
    ("fodg_all_pages_have_text", "minimal", True),
    ("fodg_all_pages_have_text", "shapes_basic", True),
    ("fodg_all_pages_have_text", "empty_page", False),
    ("fodg_average_shape_count", "minimal", 1.0),
    ("fodg_average_shape_count", "shapes_basic", 3.0),
    ("fodg_average_shape_count", "empty_page", 0.0),
    ("fodg_avg_shapes_per_nonempty_page", "minimal", 1.0),
    ("fodg_avg_shapes_per_nonempty_page", "shapes_basic", 3.0),
    ("fodg_avg_shapes_per_nonempty_page", "empty_page", 0.0),
    ("fodg_avg_shapes_per_page", "minimal", 1.0),
    ("fodg_avg_shapes_per_page", "shapes_basic", 3.0),
    ("fodg_avg_shapes_per_page", "empty_page", 0.0),
    ("fodg_avg_text_item_length", "minimal", 9.0),
    ("fodg_avg_text_item_length", "shapes_basic", 5.5),
    ("fodg_avg_text_item_length", "empty_page", 0.0),
    ("fodg_avg_text_per_page", "minimal", 9.0),
    ("fodg_avg_text_per_page", "shapes_basic", 11.0),
    ("fodg_avg_text_per_page", "empty_page", 0.0),
    ("fodg_avg_text_per_shape", "minimal", 0.0),
    ("fodg_avg_text_per_shape", "shapes_basic", 0.0),
    ("fodg_avg_text_per_shape", "empty_page", 0.0),
    ("fodg_empty_page_count", "minimal", 0),
    ("fodg_empty_page_count", "shapes_basic", 0),
    ("fodg_empty_page_count", "empty_page", 1),
    ("fodg_file_size_bytes", "minimal", 1473),
    ("fodg_file_size_bytes", "shapes_basic", 1628),
    ("fodg_file_size_bytes", "empty_page", 1053),
    ("fodg_has_at_least_one_text_item", "minimal", True),
    ("fodg_has_at_least_one_text_item", "shapes_basic", True),
    ("fodg_has_at_least_one_text_item", "empty_page", False),
    ("fodg_has_at_least_three_shapes", "minimal", False),
    ("fodg_has_at_least_three_shapes", "shapes_basic", True),
    ("fodg_has_at_least_three_shapes", "empty_page", False),
    ("fodg_has_at_least_two_shapes", "minimal", False),
    ("fodg_has_at_least_two_shapes", "shapes_basic", True),
    ("fodg_has_at_least_two_shapes", "empty_page", False),
    ("fodg_has_at_least_two_text_items", "minimal", False),
    ("fodg_has_at_least_two_text_items", "shapes_basic", True),
    ("fodg_has_at_least_two_text_items", "empty_page", False),
    ("fodg_has_empty_pages", "minimal", False),
    ("fodg_has_empty_pages", "shapes_basic", False),
    ("fodg_has_empty_pages", "empty_page", True),
    ("fodg_has_equal_shapes_and_text", "minimal", True),
    ("fodg_has_equal_shapes_and_text", "shapes_basic", False),
    ("fodg_has_equal_shapes_and_text", "empty_page", True),
    ("fodg_has_exactly_one_text_item", "minimal", True),
    ("fodg_has_exactly_one_text_item", "shapes_basic", False),
    ("fodg_has_exactly_one_text_item", "empty_page", False),
    ("fodg_has_exactly_three_shapes", "minimal", False),
    ("fodg_has_exactly_three_shapes", "shapes_basic", True),
    ("fodg_has_exactly_three_shapes", "empty_page", False),
    ("fodg_has_exactly_two_text_items", "minimal", False),
    ("fodg_has_exactly_two_text_items", "shapes_basic", True),
    ("fodg_has_exactly_two_text_items", "empty_page", False),
    ("fodg_has_mixed_content", "minimal", False),
    ("fodg_has_mixed_content", "shapes_basic", False),
    ("fodg_has_mixed_content", "empty_page", False),
    ("fodg_has_more_pages_than_shapes", "minimal", False),
    ("fodg_has_more_pages_than_shapes", "shapes_basic", False),
    ("fodg_has_more_pages_than_shapes", "empty_page", True),
    ("fodg_has_more_shapes_than_text", "minimal", False),
    ("fodg_has_more_shapes_than_text", "shapes_basic", True),
    ("fodg_has_more_shapes_than_text", "empty_page", False),
    ("fodg_has_more_shapes_than_text_items", "minimal", False),
    ("fodg_has_more_shapes_than_text_items", "shapes_basic", True),
    ("fodg_has_more_shapes_than_text_items", "empty_page", False),
    ("fodg_has_more_text_than_pages", "minimal", False),
    ("fodg_has_more_text_than_pages", "shapes_basic", True),
    ("fodg_has_more_text_than_pages", "empty_page", False),
    ("fodg_has_multiple_pages", "minimal", False),
    ("fodg_has_multiple_pages", "shapes_basic", False),
    ("fodg_has_multiple_pages", "empty_page", False),
    ("fodg_has_multiple_shapes", "minimal", False),
    ("fodg_has_multiple_shapes", "shapes_basic", True),
    ("fodg_has_multiple_shapes", "empty_page", False),
    ("fodg_has_no_shapes", "minimal", False),
    ("fodg_has_no_shapes", "shapes_basic", False),
    ("fodg_has_no_shapes", "empty_page", True),
    ("fodg_has_no_text_items", "minimal", False),
    ("fodg_has_no_text_items", "shapes_basic", False),
    ("fodg_has_no_text_items", "empty_page", True),
    ("fodg_has_non_text_shapes", "minimal", False),
    ("fodg_has_non_text_shapes", "shapes_basic", True),
    ("fodg_has_non_text_shapes", "empty_page", False),
    ("fodg_has_only_one_shape", "minimal", True),
    ("fodg_has_only_one_shape", "shapes_basic", False),
    ("fodg_has_only_one_shape", "empty_page", False),
    ("fodg_has_single_page", "minimal", True),
    ("fodg_has_single_page", "shapes_basic", True),
    ("fodg_has_single_page", "empty_page", True),
    ("fodg_has_single_shape", "minimal", True),
    ("fodg_has_single_shape", "shapes_basic", False),
    ("fodg_has_single_shape", "empty_page", False),
    ("fodg_has_text", "minimal", True),
    ("fodg_has_text", "shapes_basic", True),
    ("fodg_has_text", "empty_page", False),
    ("fodg_has_text_content", "minimal", True),
    ("fodg_has_text_content", "shapes_basic", True),
    ("fodg_has_text_content", "empty_page", False),
    ("fodg_has_text_on_all_pages", "minimal", True),
    ("fodg_has_text_on_all_pages", "shapes_basic", True),
    ("fodg_has_text_on_all_pages", "empty_page", False),
    ("fodg_has_zero_text_items", "minimal", False),
    ("fodg_has_zero_text_items", "shapes_basic", False),
    ("fodg_has_zero_text_items", "empty_page", True),
    ("fodg_installed_workflow", "minimal", {'format': 'fodg', 'loaded': True, 'page_count': 1, 'shape_count': 1}),
    ("fodg_installed_workflow", "shapes_basic", {'format': 'fodg', 'loaded': True, 'page_count': 1, 'shape_count': 3}),
    ("fodg_installed_workflow", "empty_page", {'format': 'fodg', 'loaded': True, 'page_count': 1, 'shape_count': 0}),
    ("fodg_is_empty_document", "minimal", False),
    ("fodg_is_empty_document", "shapes_basic", False),
    ("fodg_is_empty_document", "empty_page", True),
    ("fodg_is_empty_drawing", "minimal", False),
    ("fodg_is_empty_drawing", "shapes_basic", False),
    ("fodg_is_empty_drawing", "empty_page", True),
    ("fodg_is_fodg", "minimal", True),
    ("fodg_is_fodg", "shapes_basic", True),
    ("fodg_is_fodg", "empty_page", True),
    ("fodg_is_multi_page", "minimal", False),
    ("fodg_is_multi_page", "shapes_basic", False),
    ("fodg_is_multi_page", "empty_page", False),
    ("fodg_is_single_page", "minimal", True),
    ("fodg_is_single_page", "shapes_basic", True),
    ("fodg_is_single_page", "empty_page", True),
    ("fodg_is_single_shape_drawing", "minimal", True),
    ("fodg_is_single_shape_drawing", "shapes_basic", False),
    ("fodg_is_single_shape_drawing", "empty_page", False),
    ("fodg_is_text_heavy", "minimal", True),
    ("fodg_is_text_heavy", "shapes_basic", True),
    ("fodg_is_text_heavy", "empty_page", False),
    ("fodg_is_text_only", "minimal", True),
    ("fodg_is_text_only", "shapes_basic", False),
    ("fodg_is_text_only", "empty_page", False),
    ("fodg_max_shape_count", "minimal", 1),
    ("fodg_max_shape_count", "shapes_basic", 3),
    ("fodg_max_shape_count", "empty_page", 0),
    ("fodg_max_shape_text_length", "minimal", 0),
    ("fodg_max_shape_text_length", "shapes_basic", 0),
    ("fodg_max_shape_text_length", "empty_page", 0),
    ("fodg_max_shapes_per_page", "minimal", 1),
    ("fodg_max_shapes_per_page", "shapes_basic", 3),
    ("fodg_max_shapes_per_page", "empty_page", 0),
    ("fodg_max_text_item_length", "minimal", 9),
    ("fodg_max_text_item_length", "shapes_basic", 7),
    ("fodg_max_text_item_length", "empty_page", 0),
    ("fodg_max_text_per_page", "minimal", 9),
    ("fodg_max_text_per_page", "shapes_basic", 11),
    ("fodg_max_text_per_page", "empty_page", 0),
    ("fodg_min_shape_count", "minimal", 1),
    ("fodg_min_shape_count", "shapes_basic", 3),
    ("fodg_min_shape_count", "empty_page", 0),
    ("fodg_min_shapes_per_page", "minimal", 1),
    ("fodg_min_shapes_per_page", "shapes_basic", 3),
    ("fodg_min_shapes_per_page", "empty_page", 0),
    ("fodg_min_text_item_length", "minimal", 9),
    ("fodg_min_text_item_length", "shapes_basic", 4),
    ("fodg_min_text_item_length", "empty_page", 0),
    ("fodg_min_text_per_page", "minimal", 0),
    ("fodg_min_text_per_page", "shapes_basic", 0),
    ("fodg_min_text_per_page", "empty_page", 0),
    ("fodg_non_text_shape_count", "minimal", 0),
    ("fodg_non_text_shape_count", "shapes_basic", 2),
    ("fodg_non_text_shape_count", "empty_page", 0),
    ("fodg_non_text_shape_count_exceeds_page_count", "minimal", False),
    ("fodg_non_text_shape_count_exceeds_page_count", "shapes_basic", True),
    ("fodg_non_text_shape_count_exceeds_page_count", "empty_page", False),
    ("fodg_nonempty_page_count", "minimal", 1),
    ("fodg_nonempty_page_count", "shapes_basic", 1),
    ("fodg_nonempty_page_count", "empty_page", 0),
    ("fodg_nonempty_page_ratio", "minimal", 1.0),
    ("fodg_nonempty_page_ratio", "shapes_basic", 1.0),
    ("fodg_nonempty_page_ratio", "empty_page", 0.0),
    ("fodg_nonempty_shape_ratio", "minimal", 0.0),
    ("fodg_nonempty_shape_ratio", "shapes_basic", 0.0),
    ("fodg_nonempty_shape_ratio", "empty_page", 0.0),
    ("fodg_page_count", "minimal", 1),
    ("fodg_page_count", "shapes_basic", 1),
    ("fodg_page_count", "empty_page", 1),
    ("fodg_page_count_equals_shape_count", "minimal", True),
    ("fodg_page_count_equals_shape_count", "shapes_basic", False),
    ("fodg_page_count_equals_shape_count", "empty_page", False),
    ("fodg_page_count_equals_text_count", "minimal", True),
    ("fodg_page_count_equals_text_count", "shapes_basic", False),
    ("fodg_page_count_equals_text_count", "empty_page", False),
    ("fodg_page_equals_shape_count", "minimal", True),
    ("fodg_page_equals_shape_count", "shapes_basic", False),
    ("fodg_page_equals_shape_count", "empty_page", False),
    ("fodg_page_names", "minimal", ['Page1']),
    ("fodg_page_names", "shapes_basic", ['Page1']),
    ("fodg_page_names", "empty_page", ['Page1']),
    ("fodg_page_text_variance", "minimal", 0.0),
    ("fodg_page_text_variance", "shapes_basic", 0.0),
    ("fodg_page_text_variance", "empty_page", 0.0),
    ("fodg_pages_with_shapes_count", "minimal", 1),
    ("fodg_pages_with_shapes_count", "shapes_basic", 1),
    ("fodg_pages_with_shapes_count", "empty_page", 0),
    ("fodg_pages_without_shapes_count", "minimal", 0),
    ("fodg_pages_without_shapes_count", "shapes_basic", 0),
    ("fodg_pages_without_shapes_count", "empty_page", 1),
    ("fodg_shape_count_equals_page_count", "minimal", True),
    ("fodg_shape_count_equals_page_count", "shapes_basic", False),
    ("fodg_shape_count_equals_page_count", "empty_page", False),
    ("fodg_shape_count_equals_text_count", "minimal", True),
    ("fodg_shape_count_equals_text_count", "shapes_basic", False),
    ("fodg_shape_count_equals_text_count", "empty_page", True),
    ("fodg_shape_count_exceeds_text_count", "minimal", False),
    ("fodg_shape_count_exceeds_text_count", "shapes_basic", True),
    ("fodg_shape_count_exceeds_text_count", "empty_page", False),
    ("fodg_shape_count_is_one", "minimal", True),
    ("fodg_shape_count_is_one", "shapes_basic", False),
    ("fodg_shape_count_is_one", "empty_page", False),
    ("fodg_shape_count_is_three", "minimal", False),
    ("fodg_shape_count_is_three", "shapes_basic", True),
    ("fodg_shape_count_is_three", "empty_page", False),
    ("fodg_shape_count_not_equal_text_count", "minimal", False),
    ("fodg_shape_count_not_equal_text_count", "shapes_basic", True),
    ("fodg_shape_count_not_equal_text_count", "empty_page", False),
    ("fodg_shape_count_variance", "minimal", 0.0),
    ("fodg_shape_count_variance", "shapes_basic", 0.0),
    ("fodg_shape_count_variance", "empty_page", 0.0),
    ("fodg_shape_density", "minimal", 1.0),
    ("fodg_shape_density", "shapes_basic", 3.0),
    ("fodg_shape_density", "empty_page", 0.0),
    ("fodg_shape_text_ratio", "minimal", 0.0),
    ("fodg_shape_text_ratio", "shapes_basic", 0.0),
    ("fodg_shape_text_ratio", "empty_page", 0.0),
    ("fodg_shape_to_page_variance", "minimal", 0.0),
    ("fodg_shape_to_page_variance", "shapes_basic", 0.0),
    ("fodg_shape_to_page_variance", "empty_page", 0.0),
    ("fodg_shapes_exceed_pages", "minimal", False),
    ("fodg_shapes_exceed_pages", "shapes_basic", True),
    ("fodg_shapes_exceed_pages", "empty_page", False),
    ("fodg_shapes_total", "minimal", 1),
    ("fodg_shapes_total", "shapes_basic", 3),
    ("fodg_shapes_total", "empty_page", 0),
    ("fodg_shapes_with_text_count", "minimal", 0),
    ("fodg_shapes_with_text_count", "shapes_basic", 0),
    ("fodg_shapes_with_text_count", "empty_page", 0),
    ("fodg_text_and_shape_sum", "minimal", 2),
    ("fodg_text_and_shape_sum", "shapes_basic", 5),
    ("fodg_text_and_shape_sum", "empty_page", 0),
    ("fodg_text_count_equals_shape_count", "minimal", True),
    ("fodg_text_count_equals_shape_count", "shapes_basic", False),
    ("fodg_text_count_equals_shape_count", "empty_page", True),
    ("fodg_text_count_is_positive", "minimal", True),
    ("fodg_text_count_is_positive", "shapes_basic", True),
    ("fodg_text_count_is_positive", "empty_page", False),
    ("fodg_text_count_is_two", "minimal", False),
    ("fodg_text_count_is_two", "shapes_basic", True),
    ("fodg_text_count_is_two", "empty_page", False),
    ("fodg_text_count_not_equal_shape_count", "minimal", False),
    ("fodg_text_count_not_equal_shape_count", "shapes_basic", True),
    ("fodg_text_count_not_equal_shape_count", "empty_page", False),
    ("fodg_text_density", "minimal", 9.0),
    ("fodg_text_density", "shapes_basic", 3.6666666666666665),
    ("fodg_text_density", "empty_page", 0.0),
    ("fodg_text_item_count", "minimal", 1),
    ("fodg_text_item_count", "shapes_basic", 2),
    ("fodg_text_item_count", "empty_page", 0),
    ("fodg_text_item_length_range", "minimal", 0),
    ("fodg_text_item_length_range", "shapes_basic", 3),
    ("fodg_text_item_length_range", "empty_page", 0),
    ("fodg_text_item_length_sum", "minimal", 9),
    ("fodg_text_item_length_sum", "shapes_basic", 11),
    ("fodg_text_item_length_sum", "empty_page", 0),
    ("fodg_text_items_exceed_pages", "minimal", False),
    ("fodg_text_items_exceed_pages", "shapes_basic", True),
    ("fodg_text_items_exceed_pages", "empty_page", False),
    ("fodg_text_items_per_page", "minimal", [1]),
    ("fodg_text_items_per_page", "shapes_basic", [2]),
    ("fodg_text_items_per_page", "empty_page", [0]),
    ("fodg_text_items_per_shape", "minimal", 1.0),
    ("fodg_text_items_per_shape", "shapes_basic", 0.6666666666666666),
    ("fodg_text_items_per_shape", "empty_page", 0.0),
    ("fodg_text_per_shape", "minimal", 9.0),
    ("fodg_text_per_shape", "shapes_basic", 3.6666666666666665),
    ("fodg_text_per_shape", "empty_page", 0.0),
    ("fodg_text_shape_count", "minimal", 1),
    ("fodg_text_shape_count", "shapes_basic", 1),
    ("fodg_text_shape_count", "empty_page", 0),
    ("fodg_text_to_shape_ratio", "minimal", 1.0),
    ("fodg_text_to_shape_ratio", "shapes_basic", 0.3333333333333333),
    ("fodg_text_to_shape_ratio", "empty_page", 0.0),
    ("fodg_total_shape_count", "minimal", 1),
    ("fodg_total_shape_count", "shapes_basic", 3),
    ("fodg_total_shape_count", "empty_page", 0),
    ("fodg_total_shapes_and_pages", "minimal", 2),
    ("fodg_total_shapes_and_pages", "shapes_basic", 4),
    ("fodg_total_shapes_and_pages", "empty_page", 1),
    ("fodg_total_text_chars", "minimal", 0),
    ("fodg_total_text_chars", "shapes_basic", 0),
    ("fodg_total_text_chars", "empty_page", 0),
    ("fodg_total_text_items", "minimal", 1),
    ("fodg_total_text_items", "shapes_basic", 2),
    ("fodg_total_text_items", "empty_page", 0),
    ("fodg_total_text_length", "minimal", 9),
    ("fodg_total_text_length", "shapes_basic", 11),
    ("fodg_total_text_length", "empty_page", 0),
    ("fodg_unique_text_item_count", "minimal", 1),
    ("fodg_unique_text_item_count", "shapes_basic", 2),
    ("fodg_unique_text_item_count", "empty_page", 0),
    ("fodg_unique_word_count", "minimal", 0),
    ("fodg_unique_word_count", "shapes_basic", 0),
    ("fodg_unique_word_count", "empty_page", 0),
    ("fodg_word_count", "minimal", 0),
    ("fodg_word_count", "shapes_basic", 0),
    ("fodg_word_count", "empty_page", 0),
    ("get_page_metadata", "minimal", [{'name': 'Page1', 'style': '', 'master_page': '', 'shape_count': 1, 'shapes': [], 'text_content': ['Rectangle']}]),
    ("get_page_metadata", "shapes_basic", [{'name': 'Page1', 'style': '', 'master_page': '', 'shape_count': 3, 'shapes': [], 'text_content': ['Rect', 'Ellipse']}]),
    ("get_page_metadata", "empty_page", [{'name': 'Page1', 'style': '', 'master_page': '', 'shape_count': 0, 'shapes': [], 'text_content': []}]),
    ("get_shape_count", "minimal", 1),
    ("get_shape_count", "shapes_basic", 3),
    ("get_shape_count", "empty_page", 0),
    ("get_shapes", "minimal", [{'page_name': 'Page1', 'page_index': 0, 'shape_index': 0, 'tag': 'rect', 'text': 'Rectangle'}]),
    ("get_shapes", "shapes_basic", [
        {'page_name': 'Page1', 'page_index': 0, 'shape_index': 0, 'tag': 'rect', 'text': 'Rect'},
        {'page_name': 'Page1', 'page_index': 0, 'shape_index': 1, 'tag': 'ellipse', 'text': 'Ellipse'},
        {'page_name': 'Page1', 'page_index': 0, 'shape_index': 2, 'tag': 'line', 'text': ''},
    ]),
    ("get_shapes", "empty_page", []),
    ("load", "minimal", {'mime_type': 'application/vnd.oasis.opendocument.graphics-flat-xml', 'is_fodg': True, 'page_count': 1, 'pages': [{'name': 'Page1', 'style': '', 'master_page': '', 'shape_count': 1, 'shapes': [], 'text_content': ['Rectangle']}], 'shapes_total': 1}),
    ("load", "shapes_basic", {'mime_type': 'application/vnd.oasis.opendocument.graphics-flat-xml', 'is_fodg': True, 'page_count': 1, 'pages': [{'name': 'Page1', 'style': '', 'master_page': '', 'shape_count': 3, 'shapes': [], 'text_content': ['Rect', 'Ellipse']}], 'shapes_total': 3}),
    ("load", "empty_page", {'mime_type': 'application/vnd.oasis.opendocument.graphics-flat-xml', 'is_fodg': True, 'page_count': 1, 'pages': [{'name': 'Page1', 'style': '', 'master_page': '', 'shape_count': 0, 'shapes': [], 'text_content': []}], 'shapes_total': 0}),
    ("probe_fodg", "minimal", True),
    ("probe_fodg", "shapes_basic", True),
    ("probe_fodg", "empty_page", True),
]


@pytest.mark.parametrize("func_name,sample_label,expected", BULK_CASES)
def test_bulk_function_snapshot(func_name, sample_label, expected):
    """Snapshot coverage for every (source) -> value function in fodg.__all__."""
    fn = getattr(fodg, func_name, None)
    if fn is None:
        pytest.skip(f"{func_name} not exported by fodg package")
    source = SAMPLE_MAP[sample_label]
    result = fn(source)
    assert result == expected


def test_all_bulk_functions_are_exported():
    """Sanity check: every function name referenced in BULK_CASES exists on fodg."""
    names = {name for name, _, _ in BULK_CASES}
    for name in names:
        assert hasattr(fodg, name), f"fodg.{name} missing"


# ---------------------------------------------------------------------------
# Section 2 — load() edge cases and core parsing
# ---------------------------------------------------------------------------

class TestLoadEdgeCases:
    def test_load_accepts_xml_string(self):
        xml_text = MINIMAL.read_text(encoding="utf-8")
        model = fodg.load(xml_text)
        assert model["is_fodg"] is True
        assert model["page_count"] == 1

    def test_load_accepts_path_object(self):
        model = fodg.load(Path(MINIMAL))
        assert model["page_count"] == 1

    def test_load_accepts_string_path(self):
        model = fodg.load(str(MINIMAL))
        assert model["page_count"] == 1

    def test_load_oversized_bytes_raises(self):
        big = b"x" * (fodg.MAX_FILE_SIZE + 1)
        with pytest.raises(fodg.FodgError):
            fodg.load(big)

    def test_load_unsupported_type_raises(self):
        with pytest.raises(fodg.FodgError):
            fodg.load(12345)  # type: ignore[arg-type]

    def test_get_page_count_top_level(self):
        model = fodg.load(SHAPES_BASIC)
        assert fodg.get_page_count(model) == 1

    def test_get_page_count_empty_model(self):
        assert fodg.get_page_count({}) == 0


# ---------------------------------------------------------------------------
# Section 3 — create_fodg / write_fodg / roundtrip
# ---------------------------------------------------------------------------

class TestCreateWriteRoundtrip:
    def test_create_fodg_basic(self):
        model = fodg.create_fodg([{"name": "A", "texts": ["x", "y"]}, {"texts": []}])
        assert model["is_fodg"] is True
        assert model["mime_type"] == fodg.FODG_MIME
        assert model["page_count"] == 2
        assert model["pages"][0]["name"] == "A"
        assert model["pages"][0]["text_content"] == ["x", "y"]
        assert model["pages"][0]["shape_count"] == 2
        assert model["pages"][1]["name"] == "Page2"
        assert model["shapes_total"] == 2

    def test_create_fodg_empty_list(self):
        model = fodg.create_fodg([])
        assert model["page_count"] == 0
        assert model["shapes_total"] == 0
        assert model["is_fodg"] is True

    def test_create_fodg_filters_none_and_empty_texts(self):
        model = fodg.create_fodg([{"name": "P", "texts": ["ok", None, ""]}])
        assert model["pages"][0]["text_content"] == ["ok"]

    def test_write_fodg_roundtrips(self, tmp_path):
        model = fodg.load(MINIMAL)
        dest = tmp_path / "out.fodg"
        fodg.write_fodg(model, dest)
        assert dest.exists()
        assert dest.stat().st_size > 0
        reloaded = fodg.load(dest)
        assert reloaded["page_count"] == 1
        assert reloaded["is_fodg"] is True

    def test_write_fodg_non_dict_raises(self, tmp_path):
        with pytest.raises(fodg.FodgError):
            fodg.write_fodg("not-a-model", tmp_path / "x.fodg")  # type: ignore[arg-type]

    def test_write_fodg_is_fodg_false_raises(self, tmp_path):
        with pytest.raises(fodg.FodgError):
            fodg.write_fodg({"is_fodg": False, "pages": []}, tmp_path / "x.fodg")

    def test_write_fodg_accepts_created_model(self, tmp_path):
        model = fodg.create_fodg([{"name": "Solo", "texts": ["hello"]}])
        dest = tmp_path / "created.fodg"
        fodg.write_fodg(model, dest)
        reloaded = fodg.load(dest)
        assert reloaded["pages"][0]["name"] == "Solo"
        assert reloaded["pages"][0]["text_content"] == ["hello"]

    def test_roundtrip_function(self, tmp_path):
        dest = tmp_path / "rt.fodg"
        result = fodg.roundtrip(SHAPES_BASIC, dest)
        assert dest.exists()
        assert result["page_count"] == 1
        assert result["is_fodg"] is True

    def test_roundtrip_preserves_text(self, tmp_path):
        dest = tmp_path / "rt2.fodg"
        result = fodg.roundtrip(MINIMAL, dest)
        assert fodg.get_all_text(result) == ["Rectangle"]


# ---------------------------------------------------------------------------
# Section 4 — page/shape manipulation (model-based mutators)
# ---------------------------------------------------------------------------

class TestPageManipulation:
    def test_add_page_with_string_name(self):
        model = fodg.load(MINIMAL)
        new_model = fodg.add_page(model, "NewPage")
        assert new_model["page_count"] == 2
        assert new_model["pages"][-1]["name"] == "NewPage"
        assert new_model["pages"][-1]["shape_count"] == 0
        # original model is untouched (immutable API)
        assert model["page_count"] == 1

    def test_add_page_with_dict_and_texts(self):
        model = fodg.load(MINIMAL)
        new_model = fodg.add_page(model, {"name": "P2", "texts": ["hi", "bye"]})
        last = new_model["pages"][-1]
        assert last["name"] == "P2"
        assert last["text_content"] == ["hi", "bye"]
        assert last["shape_count"] == 2
        assert new_model["shapes_total"] == 3

    def test_add_page_dict_without_name_autogenerates(self):
        model = fodg.load(MINIMAL)
        new_model = fodg.add_page(model, {"texts": ["a"]})
        assert new_model["pages"][-1]["name"] == "Page2"

    def test_add_page_non_dict_model_raises(self):
        with pytest.raises(TypeError):
            fodg.add_page("not-a-model", "X")  # type: ignore[arg-type]

    def test_add_page_bad_page_or_name_type_raises(self):
        model = fodg.load(MINIMAL)
        with pytest.raises(TypeError):
            fodg.add_page(model, 12345)  # type: ignore[arg-type]

    def test_remove_page_valid(self):
        model = fodg.add_page(fodg.load(MINIMAL), "Second")
        removed = fodg.remove_page(model, 0)
        assert removed["page_count"] == 1
        assert removed["pages"][0]["name"] == "Second"

    def test_remove_page_out_of_range_raises(self):
        model = fodg.load(MINIMAL)
        with pytest.raises(fodg.FodgError):
            fodg.remove_page(model, 99)

    def test_remove_page_negative_raises(self):
        model = fodg.load(MINIMAL)
        with pytest.raises(fodg.FodgError):
            fodg.remove_page(model, -1)

    def test_remove_page_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.remove_page([], 0)  # type: ignore[arg-type]

    def test_rename_page_valid(self):
        model = fodg.load(MINIMAL)
        renamed = fodg.rename_page(model, 0, "Renamed")
        assert renamed["pages"][0]["name"] == "Renamed"
        # original untouched
        assert model["pages"][0]["name"] == "Page1"

    def test_rename_page_out_of_range_raises(self):
        model = fodg.load(MINIMAL)
        with pytest.raises(fodg.FodgError):
            fodg.rename_page(model, 5, "X")

    def test_rename_page_non_str_name_raises(self):
        model = fodg.load(MINIMAL)
        with pytest.raises(TypeError):
            fodg.rename_page(model, 0, 123)  # type: ignore[arg-type]

    def test_rename_page_non_dict_model_raises(self):
        with pytest.raises(TypeError):
            fodg.rename_page("not-a-model", 0, "X")  # type: ignore[arg-type]

    def test_duplicate_page_appends_copy(self):
        model = fodg.load(SHAPES_BASIC)
        dup = fodg.duplicate_page(model, 0)
        assert dup["page_count"] == 2
        assert dup["pages"][0] == dup["pages"][1]
        assert dup["shapes_total"] == 6

    def test_duplicate_page_out_of_range_raises(self):
        model = fodg.load(MINIMAL)
        with pytest.raises(fodg.FodgError):
            fodg.duplicate_page(model, 7)

    def test_duplicate_page_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.duplicate_page(None, 0)  # type: ignore[arg-type]

    def test_clear_page_zeroes_content(self):
        model = fodg.load(SHAPES_BASIC)
        cleared = fodg.clear_page(model, 0)
        assert cleared["pages"][0]["shape_count"] == 0
        assert cleared["pages"][0]["text_content"] == []
        assert cleared["shapes_total"] == 0

    def test_clear_page_out_of_range_raises(self):
        model = fodg.load(MINIMAL)
        with pytest.raises(fodg.FodgError):
            fodg.clear_page(model, 3)

    def test_clear_page_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.clear_page(5, 0)  # type: ignore[arg-type]

    def test_swap_pages_swaps_order(self):
        model = fodg.add_page(fodg.load(MINIMAL), "Page2")
        swapped = fodg.swap_pages(model, 0, 1)
        assert [p["name"] for p in swapped["pages"]] == ["Page2", "Page1"]

    def test_swap_pages_out_of_range_raises(self):
        model = fodg.add_page(fodg.load(MINIMAL), "Page2")
        with pytest.raises(fodg.FodgError):
            fodg.swap_pages(model, 0, 9)

    def test_swap_pages_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.swap_pages("nope", 0, 1)  # type: ignore[arg-type]

    def test_get_page_by_name_found(self):
        model = fodg.load(MINIMAL)
        page = fodg.get_page_by_name(model, "Page1")
        assert page is not None
        assert page["name"] == "Page1"

    def test_get_page_by_name_not_found(self):
        model = fodg.load(MINIMAL)
        assert fodg.get_page_by_name(model, "NoSuchPage") is None

    def test_get_page_by_name_non_dict_model_raises(self):
        with pytest.raises(TypeError):
            fodg.get_page_by_name("nope", "Page1")  # type: ignore[arg-type]

    def test_get_page_by_name_non_str_name_raises(self):
        model = fodg.load(MINIMAL)
        with pytest.raises(TypeError):
            fodg.get_page_by_name(model, 123)  # type: ignore[arg-type]

    def test_get_page_index_found(self):
        model = fodg.add_page(fodg.load(MINIMAL), "Second")
        assert fodg.get_page_index(model, "Second") == 1

    def test_get_page_index_not_found_raises(self):
        model = fodg.load(MINIMAL)
        with pytest.raises(KeyError):
            fodg.get_page_index(model, "Missing")

    def test_has_page_true_and_false(self):
        model = fodg.load(MINIMAL)
        assert fodg.has_page(model, "Page1") is True
        assert fodg.has_page(model, "Missing") is False

    def test_page_names_lists_all(self):
        model = fodg.add_page(fodg.load(MINIMAL), "Second")
        assert fodg.page_names(model) == ["Page1", "Second"]

    def test_page_names_empty_model(self):
        assert fodg.page_names({}) == []


# ---------------------------------------------------------------------------
# Section 5 — text extraction from model
# ---------------------------------------------------------------------------

class TestModelTextExtraction:
    def test_get_all_text(self):
        model = fodg.load(SHAPES_BASIC)
        assert fodg.get_all_text(model) == ["Rect", "Ellipse"]

    def test_get_all_text_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.get_all_text("nope")  # type: ignore[arg-type]

    def test_get_text_shapes(self):
        model = fodg.load(MINIMAL)
        result = fodg.get_text_shapes(model)
        assert result == [{"page_name": "Page1", "page_index": 0, "text_content": ["Rectangle"]}]

    def test_get_text_shapes_no_text_pages_excluded(self):
        model = fodg.load(EMPTY_PAGE)
        assert fodg.get_text_shapes(model) == []

    def test_get_text_shapes_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.get_text_shapes(42)  # type: ignore[arg-type]

    def test_get_page_text_valid_index(self):
        model = fodg.load(SHAPES_BASIC)
        assert fodg.get_page_text(model, 0) == ["Rect", "Ellipse"]

    def test_get_page_text_out_of_range_returns_empty(self):
        model = fodg.load(MINIMAL)
        assert fodg.get_page_text(model, 99) == []
        assert fodg.get_page_text(model, -1) == []

    def test_get_page_text_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.get_page_text("nope", 0)  # type: ignore[arg-type]

    def test_count_shapes(self):
        model = fodg.load(SHAPES_BASIC)
        assert fodg.count_shapes(model) == 3

    def test_count_shapes_missing_key_defaults_zero(self):
        assert fodg.count_shapes({}) == 0

    def test_total_text_length_model(self):
        model = fodg.load(SHAPES_BASIC)
        assert fodg.total_text_length(model) == len("Rect") + len("Ellipse")

    def test_total_text_length_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.total_text_length(None)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Section 6 — JSON export, pattern search, find_text
# ---------------------------------------------------------------------------

class TestExportAndSearch:
    def test_export_to_json_structure(self):
        model = fodg.load(MINIMAL)
        text = fodg.export_to_json(model)
        assert '"page_count": 1' in text
        assert '"Rectangle"' in text

    def test_export_page_to_json_valid(self):
        model = fodg.load(MINIMAL)
        text = fodg.export_page_to_json(model, 0)
        assert '"name": "Page1"' in text

    def test_export_page_to_json_out_of_range_returns_empty_object(self):
        model = fodg.load(MINIMAL)
        assert fodg.export_page_to_json(model, 99) == "{}"

    def test_export_page_to_json_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.export_page_to_json("nope", 0)  # type: ignore[arg-type]

    def test_export_to_csv_writes_dest(self, tmp_path):
        dest = tmp_path / "out.csv"
        csv_text = fodg.export_to_csv(SHAPES_BASIC, dest)
        assert dest.exists()
        assert dest.read_text(encoding="utf-8") == csv_text
        assert "page_name,shape_index,text" in csv_text

    def test_export_to_csv_escapes_commas_and_quotes(self, tmp_path):
        dest = tmp_path / "esc.fodg"
        model = fodg.create_fodg([{"name": "P,1", "texts": ['has "quotes", comma']}])
        fodg.write_fodg(model, dest)
        csv_text = fodg.export_to_csv(dest)
        assert '"P,1"' in csv_text
        assert '""quotes""' in csv_text

    def test_find_shapes_by_text_pattern_match(self):
        model = fodg.load(SHAPES_BASIC)
        results = fodg.find_shapes_by_text_pattern(model, "Rect")
        assert results == [{"page_idx": 0, "shape_idx": 0, "text": "Rect", "matched": True}]

    def test_find_shapes_by_text_pattern_no_match(self):
        model = fodg.load(SHAPES_BASIC)
        assert fodg.find_shapes_by_text_pattern(model, "NoSuchText") == []

    def test_find_shapes_by_text_pattern_invalid_regex_returns_empty(self):
        model = fodg.load(SHAPES_BASIC)
        assert fodg.find_shapes_by_text_pattern(model, "(unclosed") == []

    def test_find_shapes_by_text_pattern_non_dict_raises(self):
        with pytest.raises(TypeError):
            fodg.find_shapes_by_text_pattern("nope", "x")  # type: ignore[arg-type]

    def test_find_text_on_loaded_model_returns_empty(self):
        """load()'s per-page 'shapes' list is always empty; find_text iterates
        page['shapes'], so it always returns [] for models produced by load()."""
        model = fodg.load(SHAPES_BASIC)
        assert fodg.find_text(model, "Rect") == []

    def test_find_text_case_sensitivity_flag_accepted(self):
        model = fodg.load(SHAPES_BASIC)
        assert fodg.find_text(model, "rect", case_sensitive=False) == []

    def test_find_text_against_synthetic_model_with_shapes(self):
        """find_text works correctly when 'shapes' is populated directly."""
        model = {
            "pages": [
                {"name": "P1", "shapes": [{"text": "Hello World"}, {"text": "other"}]},
            ]
        }
        results = fodg.find_text(model, "Hello")
        assert results == [{"page_index": 0, "page_name": "P1", "shape_index": 0, "text": "Hello World"}]

    def test_find_text_case_insensitive_synthetic(self):
        model = {"pages": [{"name": "P1", "shapes": [{"text": "Hello World"}]}]}
        assert fodg.find_text(model, "hello", case_sensitive=False) != []
        assert fodg.find_text(model, "hello", case_sensitive=True) == []


# ---------------------------------------------------------------------------
# Section 7 — module-level constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_fodg_mime_constant(self):
        assert fodg.FODG_MIME == "application/vnd.oasis.opendocument.graphics-flat-xml"

    def test_max_file_size_constant(self):
        assert fodg.MAX_FILE_SIZE == 64 * 1024 * 1024

    def test_ns_dict_has_expected_prefixes(self):
        assert set(fodg.NS.keys()) >= {"office", "draw", "text", "style"}

    def test_shape_tags_is_nonempty_set(self):
        assert isinstance(fodg.SHAPE_TAGS, (set, frozenset))
        assert len(fodg.SHAPE_TAGS) > 0

    def test_spec_qname_constant(self):
        assert fodg.spec_qname == "office:document"

    def test_spec_fact_ref_constant(self):
        assert fodg.spec_fact_ref == "SAL-FODG-00001"

    def test_namespace_uri_constant(self):
        assert fodg.namespace_uri == "urn:oasis:names:tc:opendocument:xmlns:office:1.0"


# ---------------------------------------------------------------------------
# Section 8 — models.FodgDocument (typed domain wrapper)
# ---------------------------------------------------------------------------

class TestFodgDocumentModel:
    def test_from_file_and_basic_properties(self):
        doc = FodgDocument.from_file(SHAPES_BASIC)
        assert doc.page_count == 1
        assert doc.shapes_total == 3
        assert doc.is_fodg is True

    def test_pages_property_returns_list_copy(self):
        doc = FodgDocument.from_file(MINIMAL)
        pages = doc.pages
        assert isinstance(pages, list)
        assert pages[0]["name"] == "Page1"

    def test_is_empty_true_for_zero_pages(self):
        doc = FodgDocument({"page_count": 0, "shapes_total": 0, "pages": []})
        assert doc.is_empty is True
        assert doc.is_single_page is False
        assert doc.has_shapes is False

    def test_is_single_page_true(self):
        doc = FodgDocument.from_file(MINIMAL)
        assert doc.is_single_page is True
        assert doc.is_multi_page is False

    def test_has_shapes_and_has_multiple_shapes(self):
        doc = FodgDocument.from_file(SHAPES_BASIC)
        assert doc.has_shapes is True
        assert doc.has_multiple_shapes is True

    def test_shapes_per_page_zero_pages(self):
        doc = FodgDocument({"page_count": 0, "shapes_total": 0, "pages": []})
        assert doc.shapes_per_page == 0.0

    def test_shapes_per_page_computed(self):
        doc = FodgDocument.from_file(SHAPES_BASIC)
        assert doc.shapes_per_page == 3.0

    def test_is_dense_threshold(self):
        doc = FodgDocument({"page_count": 1, "shapes_total": 11, "pages": [{"shape_count": 11}]})
        assert doc.is_dense is True
        doc2 = FodgDocument.from_file(SHAPES_BASIC)
        assert doc2.is_dense is False

    def test_is_complex_requires_shapes_and_multi_page(self):
        doc = FodgDocument.from_file(SHAPES_BASIC)
        assert doc.is_complex is False  # single page

    def test_max_min_shape_range_no_pages(self):
        doc = FodgDocument({"pages": []})
        assert doc.max_shapes_on_page == 0
        assert doc.min_shapes_on_page == 0
        assert doc.shape_range == 0
        assert doc.is_uniform_density is True

    def test_max_min_shape_range_with_pages(self):
        doc = FodgDocument({"pages": [{"shape_count": 5}, {"shape_count": 2}]})
        assert doc.max_shapes_on_page == 5
        assert doc.min_shapes_on_page == 2
        assert doc.shape_range == 3
        assert doc.is_uniform_density is False

    def test_is_uniform_density_true_when_equal(self):
        doc = FodgDocument({"pages": [{"shape_count": 2}, {"shape_count": 2}]})
        assert doc.is_uniform_density is True

    def test_add_page_default_name_and_texts(self):
        doc = FodgDocument.from_file(MINIMAL)
        doc.add_page()
        assert doc.page_count == 2
        assert doc.pages[-1]["name"] == "Page2"
        assert doc.pages[-1]["text_content"] == []

    def test_add_page_with_name_and_texts(self):
        doc = FodgDocument.from_file(MINIMAL)
        doc.add_page("Extra", ["t1"])
        assert doc.pages[-1]["name"] == "Extra"
        assert doc.pages[-1]["text_content"] == ["t1"]
        assert doc.shapes_total == 2

    def test_add_page_bad_name_type_raises(self):
        doc = FodgDocument.from_file(MINIMAL)
        with pytest.raises(fodg.FodgError):
            doc.add_page(123)  # type: ignore[arg-type]

    def test_save_to_file_creates_parents(self, tmp_path):
        doc = FodgDocument.from_file(MINIMAL)
        out = tmp_path / "nested" / "dir" / "saved.fodg"
        doc.save_to_file(out)
        assert out.exists()
        reloaded = FodgDocument.from_file(out)
        assert reloaded.page_count == 1

    def test_save_to_file_empty_path_raises(self):
        doc = FodgDocument.from_file(MINIMAL)
        with pytest.raises(fodg.FodgError):
            doc.save_to_file("")

    def test_to_dict_summary(self):
        doc = FodgDocument.from_file(SHAPES_BASIC)
        summary = doc.to_dict()
        assert summary == {"is_fodg": True, "page_count": 1, "shapes_total": 3}

    def test_repr_contains_page_and_shape_counts(self):
        doc = FodgDocument.from_file(SHAPES_BASIC)
        text = repr(doc)
        assert "page_count=1" in text
        assert "shapes_total=3" in text

    def test_spec_metadata_classvars(self):
        assert FodgDocument.spec_qname == "office:document"
        assert FodgDocument.spec_fact_ref == "SAL-FODG-00001"
        assert FodgDocument.namespace_uri == "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
        assert FodgDocument.local_name == "document"


# ---------------------------------------------------------------------------
# Section 9 — Compat facades (FodgDocument / FodgPage) and spec.draw.Page
# ---------------------------------------------------------------------------

class TestCompatFacades:
    def test_compat_import_path(self):
        from fodg.Compat import FodgDocument as CompatDocument
        from fodg.Compat import FodgPage as CompatPage
        assert CompatDocument is not None
        assert CompatPage is not None

    def test_compat_document_from_file(self):
        from fodg.Compat import FodgDocument as CompatDocument
        doc = CompatDocument.from_file(str(SHAPES_BASIC))
        assert doc.page_count == 1

    def test_compat_document_page_objects(self):
        from fodg.Compat import FodgDocument as CompatDocument
        from fodg.spec.draw.page import Page as SpecPage
        doc = CompatDocument.from_file(str(SHAPES_BASIC))
        pages = doc.page_objects()
        assert len(pages) == 1
        assert isinstance(pages[0], SpecPage)
        assert pages[0].name == "Page1"
        assert pages[0].shape_count == 3

    def test_compat_document_spec_metadata(self):
        from fodg.Compat import FodgDocument as CompatDocument
        assert CompatDocument.spec_qname == "office:document"
        assert CompatDocument.spec_fact_ref == "SAL-FODG-00031"
        assert CompatDocument.namespace_uri == "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    def test_compat_page_spec_metadata(self):
        from fodg.Compat import FodgPage as CompatPage
        assert CompatPage.spec_qname == "draw:page"
        assert CompatPage.spec_fact_ref == "SAL-FODG-00414"
        assert CompatPage.namespace_uri == "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"

    def test_spec_page_direct_construction(self):
        from fodg.spec.draw.page import Page as SpecPage
        page = SpecPage({"name": "X", "shape_count": 4, "shapes": []})
        assert page.name == "X"
        assert page.shape_count == 4
        assert page.shapes == []
        assert page.to_dict() == {"name": "X", "shape_count": 4, "shapes": []}
        assert "X" in repr(page)

    def test_spec_page_defaults_when_missing_keys(self):
        from fodg.spec.draw.page import Page as SpecPage
        page = SpecPage({})
        assert page.name == ""
        assert page.shape_count == 0
        assert page.shapes == []


# ---------------------------------------------------------------------------
# Section 10 — fodg_page_iterator.fodg_iter_pages
# ---------------------------------------------------------------------------

class TestPageIterator:
    def test_iter_pages_yields_page_objects(self):
        from fodg.spec.draw.page import Page as SpecPage
        pages = list(fodg.fodg_iter_pages(SHAPES_BASIC))
        assert len(pages) == 1
        assert isinstance(pages[0], SpecPage)
        assert pages[0].name == "Page1"
        assert pages[0].shape_count == 3

    def test_iter_pages_empty_document(self):
        pages = list(fodg.fodg_iter_pages(EMPTY_PAGE))
        assert len(pages) == 1
        assert pages[0].shape_count == 0

    def test_iter_pages_is_lazy_generator(self):
        gen = fodg.fodg_iter_pages(MINIMAL)
        import types
        assert isinstance(gen, types.GeneratorType)


# ---------------------------------------------------------------------------
# Section 11 — fodg_workflow.fodg_installed_workflow (also covered in bulk,
# additional direct-call assertions here for clarity)
# ---------------------------------------------------------------------------

class TestInstalledWorkflow:
    def test_installed_workflow_accepts_bytes(self):
        data = SHAPES_BASIC.read_bytes()
        result = fodg.fodg_installed_workflow(data)
        assert result["format"] == "fodg"
        assert result["loaded"] is True
        assert result["shape_count"] == 3


# ---------------------------------------------------------------------------
# Section 12 — exceptions.py hierarchy (not wired into fodg_codec's error
# raising — fodg_codec.py defines its own separate FodgError/FodgParseError
# hierarchy that IS what fodg.FodgError resolves to at the package level).
# ---------------------------------------------------------------------------

class TestExceptionsModule:
    def test_fodg_error_is_exception(self):
        assert issubclass(fodg_exceptions.FodgError, Exception)

    def test_fodg_parse_error_subclasses_fodg_error(self):
        assert issubclass(fodg_exceptions.FodgParseError, fodg_exceptions.FodgError)

    def test_fodg_write_error_subclasses_fodg_error(self):
        assert issubclass(fodg_exceptions.FodgWriteError, fodg_exceptions.FodgError)

    def test_exceptions_module_fodg_error_distinct_from_codec_fodg_error(self):
        """fodg_codec.py and exceptions.py define separate FodgError classes;
        the package-level fodg.FodgError resolves to the fodg_codec one."""
        assert fodg_exceptions.FodgError is not fodg.FodgError

    def test_can_raise_and_catch_exceptions_module_errors(self):
        with pytest.raises(fodg_exceptions.FodgError):
            raise fodg_exceptions.FodgParseError("boom")
        with pytest.raises(fodg_exceptions.FodgError):
            raise fodg_exceptions.FodgWriteError("boom")

    def test_codec_fodg_parse_error_subclasses_codec_fodg_error(self):
        assert issubclass(fodg.FodgParseError, fodg.FodgError)


# ---------------------------------------------------------------------------
# Section 13 — cli.py entry point
# ---------------------------------------------------------------------------

class TestCli:
    def test_main_no_args_prints_usage_and_exits_zero(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["ff-fodg"])
        with pytest.raises(SystemExit) as exc_info:
            fodg_cli.main()
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "Usage: ff-fodg FILE.fodg" in out

    def test_main_missing_file_exits_one(self, monkeypatch, capsys, tmp_path):
        missing = tmp_path / "does-not-exist.fodg"
        monkeypatch.setattr(sys, "argv", ["ff-fodg", str(missing)])
        with pytest.raises(SystemExit) as exc_info:
            fodg_cli.main()
        assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "file not found" in err

    def test_main_existing_file_hits_broken_load_fodg_import(self, monkeypatch):
        """cli.py imports `load_fodg` from the fodg package, but the package
        only exports `load` — this is a known bug. main() raises ImportError
        (uncaught, not the SystemExit(2) the except-block would otherwise
        produce) for any existing file path. Documented as current behavior."""
        monkeypatch.setattr(sys, "argv", ["ff-fodg", str(MINIMAL)])
        with pytest.raises(ImportError):
            fodg_cli.main()
