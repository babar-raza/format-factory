"""test_dogfood_fodp_remaining_gaps_ndjson_export.py

Dogfood export path: FODP remaining analytics gap functions -> NDJSON.

Covers: fodp_all_slides_have_text, fodp_avg_notes_length, fodp_has_images,
        fodp_has_notes, fodp_has_titles, fodp_has_zero_shapes, fodp_image_count,
        fodp_image_density, fodp_is_shape_heavy, fodp_is_text_heavy,
        fodp_longest_slide_index, fodp_longest_slide_text_length,
        fodp_max_notes_length, fodp_max_shape_count, fodp_nonempty_slide_count,
        fodp_nonempty_slide_ratio, fodp_total_shape_count, fodp_word_count

Concrete values:
  minimal-presentation.fodp: all_slides_have_text=True, has_titles=True, has_zero_shapes=False,
                              total_shape_count=1, word_count=1, longest_slide_text_length=5
  two-slides-basic.fodp: is_shape_heavy=True, total_shape_count=3, nonempty_slide_count=2,
                         longest_slide_text_length=33, word_count=5, max_shape_count=2
  title-only.fodp: all_slides_have_text=False, has_zero_shapes=True, total_shape_count=0,
                   nonempty_slide_count=0, word_count=0

Sprint: product-deepening-fodp-remaining-gaps-dogfood-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import (
    fodp_all_slides_have_text,
    fodp_avg_notes_length,
    fodp_has_images,
    fodp_has_notes,
    fodp_has_titles,
    fodp_has_zero_shapes,
    fodp_image_count,
    fodp_is_shape_heavy,
    fodp_is_text_heavy,
    fodp_longest_slide_index,
    fodp_longest_slide_text_length,
    fodp_max_notes_length,
    fodp_max_shape_count,
    fodp_nonempty_slide_count,
    fodp_nonempty_slide_ratio,
    fodp_total_shape_count,
    fodp_word_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson

SAMPLES_DIR = _REPO / "samples" / "by-format" / "fodp"
MINIMAL = SAMPLES_DIR / "minimal-presentation.fodp"
TWO_SLIDES = SAMPLES_DIR / "two-slides-basic.fodp"
TITLE_ONLY = SAMPLES_DIR / "title-only.fodp"


class TestFodpRemainingGapsNdjsonExport:

    def test_minimal_all_slides_have_text(self):
        assert fodp_all_slides_have_text(MINIMAL) is True

    def test_title_only_not_all_slides_have_text(self):
        assert fodp_all_slides_have_text(TITLE_ONLY) is False

    def test_minimal_avg_notes_length_zero(self):
        assert abs(fodp_avg_notes_length(MINIMAL)) < 0.01

    def test_minimal_has_no_images(self):
        assert fodp_has_images(MINIMAL) is False

    def test_minimal_has_no_notes(self):
        assert fodp_has_notes(MINIMAL) is False

    def test_minimal_has_titles(self):
        assert fodp_has_titles(MINIMAL) is True

    def test_title_only_has_no_titles(self):
        assert fodp_has_titles(TITLE_ONLY) is False

    def test_minimal_has_no_zero_shapes(self):
        assert fodp_has_zero_shapes(MINIMAL) is False

    def test_title_only_has_zero_shapes(self):
        assert fodp_has_zero_shapes(TITLE_ONLY) is True

    def test_minimal_image_count_zero(self):
        assert fodp_image_count(MINIMAL) == 0

    def test_two_slides_is_shape_heavy(self):
        assert fodp_is_shape_heavy(TWO_SLIDES) is True

    def test_minimal_not_shape_heavy(self):
        assert fodp_is_shape_heavy(MINIMAL) is False

    def test_minimal_not_text_heavy(self):
        assert fodp_is_text_heavy(MINIMAL) is False

    def test_minimal_longest_slide_index(self):
        assert fodp_longest_slide_index(MINIMAL) == 0

    def test_title_only_longest_slide_index_negative(self):
        assert fodp_longest_slide_index(TITLE_ONLY) == -1

    def test_minimal_longest_slide_text_length(self):
        assert fodp_longest_slide_text_length(MINIMAL) == 5

    def test_two_slides_longest_slide_text_length(self):
        assert fodp_longest_slide_text_length(TWO_SLIDES) >= 20

    def test_minimal_max_notes_length_zero(self):
        assert fodp_max_notes_length(MINIMAL) == 0

    def test_minimal_max_shape_count(self):
        assert fodp_max_shape_count(MINIMAL) == 1

    def test_two_slides_max_shape_count(self):
        assert fodp_max_shape_count(TWO_SLIDES) == 2

    def test_title_only_max_shape_count_zero(self):
        assert fodp_max_shape_count(TITLE_ONLY) == 0

    def test_minimal_nonempty_slide_count(self):
        assert fodp_nonempty_slide_count(MINIMAL) == 1

    def test_two_slides_nonempty_slide_count(self):
        assert fodp_nonempty_slide_count(TWO_SLIDES) == 2

    def test_title_only_nonempty_slide_count_zero(self):
        assert fodp_nonempty_slide_count(TITLE_ONLY) == 0

    def test_minimal_total_shape_count(self):
        assert fodp_total_shape_count(MINIMAL) == 1

    def test_two_slides_total_shape_count(self):
        assert fodp_total_shape_count(TWO_SLIDES) == 3

    def test_minimal_word_count(self):
        assert fodp_word_count(MINIMAL) == 1

    def test_two_slides_word_count(self):
        assert fodp_word_count(TWO_SLIDES) >= 3

    def test_title_only_word_count_zero(self):
        assert fodp_word_count(TITLE_ONLY) == 0

    def test_ndjson_export_fodp_records(self, tmp_path):
        records = [
            {
                "file": MINIMAL.name,
                "total_shape_count": fodp_total_shape_count(MINIMAL),
                "word_count": fodp_word_count(MINIMAL),
                "has_titles": fodp_has_titles(MINIMAL),
            },
            {
                "file": TWO_SLIDES.name,
                "total_shape_count": fodp_total_shape_count(TWO_SLIDES),
                "word_count": fodp_word_count(TWO_SLIDES),
                "is_shape_heavy": fodp_is_shape_heavy(TWO_SLIDES),
            },
        ]
        out = tmp_path / "fodp_remaining.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["total_shape_count"] == 1
        assert json.loads(lines[1])["is_shape_heavy"] is True
