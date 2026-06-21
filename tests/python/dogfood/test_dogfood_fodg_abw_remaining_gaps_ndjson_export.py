"""test_dogfood_fodg_abw_remaining_gaps_ndjson_export.py

Dogfood export path: FODG remaining + ABW remaining analytics gap functions -> NDJSON.

Covers FODG: fodg_all_pages_have_shapes, fodg_avg_shapes_per_nonempty_page,
             fodg_avg_shapes_per_page, fodg_avg_text_per_shape, fodg_empty_page_count,
             fodg_has_empty_pages, fodg_has_no_shapes, fodg_has_non_text_shapes,
             fodg_has_single_shape, fodg_is_empty_document, fodg_is_multi_page,
             fodg_max_shape_text_length, fodg_nonempty_page_count, fodg_total_shape_count
Covers ABW: abw_avg_sentence_word_count, abw_capital_word_count, abw_digit_count,
            abw_paragraph_density, abw_unique_char_count

Concrete values:
  empty-page.fodg: all_pages_have_shapes=False, has_empty_pages=True, is_empty=True,
                   empty_page_count=1, nonempty_page_count=0, total_shape_count=0
  minimal-drawing.fodg: all_pages_have_shapes=True, has_single_shape=True, total_shape_count=1
  shapes-basic.fodg: has_non_text_shapes=True, total_shape_count=3, avg_shapes_per_page=3.0
  ABW minimal: avg_sentence_word_count=1.0, capital_word_count=1, digit_count=0, unique_char_count=4
  ABW two-paragraphs: avg_sentence_word_count=2.0, capital_word_count=2
  ABW empty-section: avg_sentence_word_count=0.0, capital_word_count=0

Sprint: product-deepening-fodg-abw-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_all_pages_have_shapes,
    fodg_avg_shapes_per_nonempty_page,
    fodg_avg_shapes_per_page,
    fodg_avg_text_per_shape,
    fodg_empty_page_count,
    fodg_has_empty_pages,
    fodg_has_no_shapes,
    fodg_has_non_text_shapes,
    fodg_has_single_shape,
    fodg_is_empty_document,
    fodg_is_multi_page,
    fodg_max_shape_text_length,
    fodg_nonempty_page_count,
    fodg_total_shape_count,
)
from src.python.abw.abw_codec import (
    abw_avg_sentence_word_count,
    abw_capital_word_count,
    abw_digit_count,
    abw_paragraph_density,
    abw_unique_char_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson

FODG_DIR = _REPO / "samples" / "by-format" / "fodg"
ABW_DIR = _REPO / "samples" / "by-format" / "abw"

FODG_EMPTY = FODG_DIR / "empty-page.fodg"
FODG_MINIMAL = FODG_DIR / "minimal-drawing.fodg"
FODG_SHAPES = FODG_DIR / "shapes-basic.fodg"
ABW_MINIMAL = ABW_DIR / "minimal-document.abw"
ABW_TWO_PARA = ABW_DIR / "two-paragraphs.abw"
ABW_EMPTY = ABW_DIR / "empty-section.abw"


class TestFodgAbwRemainingGapsNdjsonExport:

    # FODG tests
    def test_empty_page_all_pages_have_shapes_false(self):
        assert fodg_all_pages_have_shapes(FODG_EMPTY) is False

    def test_minimal_all_pages_have_shapes_true(self):
        assert fodg_all_pages_have_shapes(FODG_MINIMAL) is True

    def test_empty_page_has_empty_pages(self):
        assert fodg_has_empty_pages(FODG_EMPTY) is True

    def test_minimal_has_no_empty_pages(self):
        assert fodg_has_empty_pages(FODG_MINIMAL) is False

    def test_empty_page_has_no_shapes(self):
        assert fodg_has_no_shapes(FODG_EMPTY) is True

    def test_minimal_has_shapes(self):
        assert fodg_has_no_shapes(FODG_MINIMAL) is False

    def test_shapes_has_non_text_shapes(self):
        assert fodg_has_non_text_shapes(FODG_SHAPES) is True

    def test_minimal_has_single_shape(self):
        assert fodg_has_single_shape(FODG_MINIMAL) is True

    def test_shapes_not_single_shape(self):
        assert fodg_has_single_shape(FODG_SHAPES) is False

    def test_empty_page_is_empty_document(self):
        assert fodg_is_empty_document(FODG_EMPTY) is True

    def test_minimal_not_empty_document(self):
        assert fodg_is_empty_document(FODG_MINIMAL) is False

    def test_empty_total_shape_count_zero(self):
        assert fodg_total_shape_count(FODG_EMPTY) == 0

    def test_minimal_total_shape_count_one(self):
        assert fodg_total_shape_count(FODG_MINIMAL) == 1

    def test_shapes_total_shape_count_three(self):
        assert fodg_total_shape_count(FODG_SHAPES) == 3

    def test_shapes_avg_shapes_per_page(self):
        assert abs(fodg_avg_shapes_per_page(FODG_SHAPES) - 3.0) < 0.01

    def test_empty_nonempty_page_count_zero(self):
        assert fodg_nonempty_page_count(FODG_EMPTY) == 0

    def test_minimal_nonempty_page_count_one(self):
        assert fodg_nonempty_page_count(FODG_MINIMAL) == 1

    def test_empty_empty_page_count_one(self):
        assert fodg_empty_page_count(FODG_EMPTY) == 1

    def test_minimal_empty_page_count_zero(self):
        assert fodg_empty_page_count(FODG_MINIMAL) == 0

    def test_empty_max_shape_text_length_zero(self):
        assert fodg_max_shape_text_length(FODG_EMPTY) == 0

    # ABW tests
    def test_abw_minimal_avg_sentence_word_count(self):
        assert abs(abw_avg_sentence_word_count(ABW_MINIMAL) - 1.0) < 0.01

    def test_abw_two_para_avg_sentence_word_count(self):
        assert abs(abw_avg_sentence_word_count(ABW_TWO_PARA) - 2.0) < 0.01

    def test_abw_empty_avg_sentence_word_count_zero(self):
        assert abs(abw_avg_sentence_word_count(ABW_EMPTY)) < 0.01

    def test_abw_minimal_capital_word_count(self):
        assert abw_capital_word_count(ABW_MINIMAL) == 1

    def test_abw_minimal_digit_count_zero(self):
        assert abw_digit_count(ABW_MINIMAL) == 0

    def test_abw_minimal_unique_char_count(self):
        assert abw_unique_char_count(ABW_MINIMAL) == 4

    def test_abw_two_para_unique_char_count(self):
        assert abw_unique_char_count(ABW_TWO_PARA) == 17

    def test_abw_empty_paragraph_density_zero(self):
        assert abs(abw_paragraph_density(ABW_EMPTY)) < 0.01

    def test_ndjson_export_fodg_record(self, tmp_path):
        records = [{
            "file": FODG_SHAPES.name,
            "total_shape_count": fodg_total_shape_count(FODG_SHAPES),
            "has_non_text_shapes": fodg_has_non_text_shapes(FODG_SHAPES),
            "avg_shapes_per_page": fodg_avg_shapes_per_page(FODG_SHAPES),
        }]
        out = tmp_path / "fodg_remaining.ndjson"
        write_ndjson(records, str(out))
        parsed = json.loads(out.read_text(encoding="utf-8").strip())
        assert parsed["total_shape_count"] == 3

    def test_ndjson_export_abw_records(self, tmp_path):
        records = [
            {"file": ABW_MINIMAL.name, "capital_word_count": abw_capital_word_count(ABW_MINIMAL)},
            {"file": ABW_TWO_PARA.name, "capital_word_count": abw_capital_word_count(ABW_TWO_PARA)},
        ]
        out = tmp_path / "abw_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["capital_word_count"] == 1
        assert json.loads(lines[1])["capital_word_count"] == 2
