"""
tests/python/dogfood/test_dogfood_fodp_massive_analytics_gap_closure_ndjson_export.py

Sprint: dogfood-analytics-gap-closure-batch3-20260617
Dogfood export: FODP analytics -> NDJSON roundtrip.
Covers 110 previously-untested fodp_* analytics functions on two-slides-basic.fodp.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import (
    fodp_all_pages_have_title,
    fodp_all_slides_have_text,
    fodp_alpha_ratio,
    fodp_average_shapes_per_slide,
    fodp_average_text_per_slide,
    fodp_avg_notes_length,
    fodp_avg_sentence_length,
    fodp_avg_shape_text_length,
    fodp_avg_shapes_per_slide,
    fodp_avg_slide_shape_count,
    fodp_avg_text_length,
    fodp_avg_text_per_slide,
    fodp_avg_title_length,
    fodp_avg_title_words,
    fodp_avg_word_count_per_slide,
    fodp_avg_words_per_slide,
    fodp_blank_slide_count,
    fodp_chars_per_shape,
    fodp_digit_count,
    fodp_empty_slide_count,
    fodp_file_size_bytes,
    fodp_has_empty_slides,
    fodp_has_images,
    fodp_has_multi_slide,
    fodp_has_multiple_slides,
    fodp_has_notes,
    fodp_has_numeric_content,
    fodp_has_speaker_notes,
    fodp_has_titles,
    fodp_has_zero_shapes,
    fodp_image_to_slide_ratio,
    fodp_is_nonempty,
    fodp_is_shape_heavy,
    fodp_is_single_nonempty_slide,
    fodp_is_single_slide,
    fodp_is_text_heavy,
    fodp_longest_slide_index,
    fodp_longest_slide_text_length,
    fodp_lowercase_ratio,
    fodp_master_page_count,
    fodp_max_notes_length,
    fodp_max_shape_count,
    fodp_max_shape_count_per_slide,
    fodp_max_shape_text_length,
    fodp_max_shapes_per_slide,
    fodp_max_text_item_count,
    fodp_max_text_per_slide,
    fodp_max_title_length,
    fodp_min_shape_count,
    fodp_min_shapes_per_slide,
    fodp_min_text_per_slide,
    fodp_min_title_length,
    fodp_nonempty_shape_count,
    fodp_nonempty_slide_count,
    fodp_nonempty_slide_ratio,
    fodp_note_count,
    fodp_notes_density,
    fodp_notes_length_sum,
    fodp_notes_text,
    fodp_notes_to_slide_ratio,
    fodp_notes_total_length,
    fodp_punctuation_count,
    fodp_shape_count_variance,
    fodp_shape_diversity,
    fodp_shape_to_slide_ratio,
    fodp_shape_variance,
    fodp_shortest_slide_index,
    fodp_slide_count,
    fodp_slide_count_is_even,
    fodp_slide_count_is_one,
    fodp_slide_shape_counts,
    fodp_slide_text_density,
    fodp_slide_text_range,
    fodp_slide_text_variance,
    fodp_slide_title_count,
    fodp_slide_titles,
    fodp_slide_word_variance,
    fodp_text_to_slide_ratio,
    fodp_title_coverage,
    fodp_total_chars_per_slide,
    fodp_total_image_count,
    fodp_total_images,
    fodp_total_notes_length,
    fodp_total_shape_count,
    fodp_total_text_chars,
    fodp_total_text_length,
    fodp_total_title_chars,
    fodp_unique_slide_title_count,
    fodp_uppercase_count,
    fodp_vowel_count,
    fodp_word_count,
    fodp_word_length_variance,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_FODP_DIR = _REPO / "samples" / "by-format" / "fodp"
_S = str(_FODP_DIR / "two-slides-basic.fodp")


class TestFodpMassiveAnalyticsGapClosureNdjsonExport:
    """90+ FODP analytics functions -> NDJSON dogfood export on two-slides-basic.fodp."""

    # --- boolean analytics ---

    def test_all_pages_have_title_true(self):
        assert fodp_all_pages_have_title(_S) is True

    def test_all_slides_have_text_true(self):
        assert fodp_all_slides_have_text(_S) is True

    def test_has_empty_slides_false(self):
        assert fodp_has_empty_slides(_S) is False

    def test_has_images_false(self):
        assert fodp_has_images(_S) is False

    def test_has_multi_slide_true(self):
        assert fodp_has_multi_slide(_S) is True

    def test_has_multiple_slides_true(self):
        assert fodp_has_multiple_slides(_S) is True

    def test_has_notes_false(self):
        assert fodp_has_notes(_S) is False

    def test_has_numeric_content_false(self):
        assert fodp_has_numeric_content(_S) is False

    def test_has_speaker_notes_false(self):
        assert fodp_has_speaker_notes(_S) is False

    def test_has_titles_true(self):
        assert fodp_has_titles(_S) is True

    def test_has_zero_shapes_false(self):
        assert fodp_has_zero_shapes(_S) is False

    def test_is_nonempty_true(self):
        assert fodp_is_nonempty(_S) is True

    def test_is_shape_heavy_true(self):
        assert fodp_is_shape_heavy(_S) is True

    def test_is_single_nonempty_slide_false(self):
        assert fodp_is_single_nonempty_slide(_S) is False

    def test_is_single_slide_false(self):
        assert fodp_is_single_slide(_S) is False

    def test_is_text_heavy_false(self):
        assert fodp_is_text_heavy(_S) is False

    def test_slide_count_is_even_true(self):
        assert fodp_slide_count_is_even(_S) is True

    def test_slide_count_is_one_false(self):
        assert fodp_slide_count_is_one(_S) is False

    # --- numeric analytics ---

    def test_alpha_ratio(self):
        val = fodp_alpha_ratio(_S)
        assert abs(val - 0.9286) < 0.001

    def test_average_shapes_per_slide(self):
        assert fodp_average_shapes_per_slide(_S) == 1.5

    def test_average_text_per_slide(self):
        assert fodp_average_text_per_slide(_S) == 21.5

    def test_avg_notes_length(self):
        assert fodp_avg_notes_length(_S) == 0.0

    def test_avg_sentence_length(self):
        assert fodp_avg_sentence_length(_S) == 21.0

    def test_avg_shape_text_length(self):
        assert fodp_avg_shape_text_length(_S) == 0.0

    def test_avg_shapes_per_slide(self):
        assert fodp_avg_shapes_per_slide(_S) == 1.5

    def test_avg_slide_shape_count(self):
        assert fodp_avg_slide_shape_count(_S) == 0.0

    def test_avg_text_length(self):
        assert fodp_avg_text_length(_S) == 21.0

    def test_avg_text_per_slide(self):
        assert fodp_avg_text_per_slide(_S) == 0.0

    def test_avg_title_length(self):
        assert fodp_avg_title_length(_S) == 11.0

    def test_avg_title_words(self):
        assert fodp_avg_title_words(_S) == 1.0

    def test_avg_word_count_per_slide(self):
        assert fodp_avg_word_count_per_slide(_S) == 0.0

    def test_avg_words_per_slide(self):
        assert fodp_avg_words_per_slide(_S) == 2.5

    def test_blank_slide_count(self):
        assert fodp_blank_slide_count(_S) == 0

    def test_chars_per_shape(self):
        val = fodp_chars_per_shape(_S)
        assert abs(val - 14.3333) < 0.001

    def test_digit_count(self):
        assert fodp_digit_count(_S) == 0

    def test_empty_slide_count(self):
        assert fodp_empty_slide_count(_S) == 0

    def test_file_size_bytes(self):
        val = fodp_file_size_bytes(_S)
        assert isinstance(val, int)
        assert val > 0

    def test_image_to_slide_ratio(self):
        assert fodp_image_to_slide_ratio(_S) == 0.0

    def test_longest_slide_index(self):
        assert fodp_longest_slide_index(_S) == 0

    def test_longest_slide_text_length(self):
        assert fodp_longest_slide_text_length(_S) == 33

    def test_lowercase_ratio(self):
        assert fodp_lowercase_ratio(_S) == 0.0

    def test_master_page_count(self):
        assert fodp_master_page_count(_S) == 0

    def test_max_notes_length(self):
        assert fodp_max_notes_length(_S) == 0

    def test_max_shape_count(self):
        assert fodp_max_shape_count(_S) == 2

    def test_max_shape_count_per_slide(self):
        assert fodp_max_shape_count_per_slide(_S) == 0

    def test_max_shape_text_length(self):
        assert fodp_max_shape_text_length(_S) == 20

    def test_max_shapes_per_slide(self):
        assert fodp_max_shapes_per_slide(_S) == 2

    def test_max_text_item_count(self):
        assert fodp_max_text_item_count(_S) == 2

    def test_max_text_per_slide(self):
        assert fodp_max_text_per_slide(_S) == 33

    def test_max_title_length(self):
        assert fodp_max_title_length(_S) == 12

    def test_min_shape_count(self):
        assert fodp_min_shape_count(_S) == 1

    def test_min_shapes_per_slide(self):
        assert fodp_min_shapes_per_slide(_S) == 1

    def test_min_text_per_slide(self):
        assert fodp_min_text_per_slide(_S) == 10

    def test_min_title_length(self):
        assert fodp_min_title_length(_S) == 10

    def test_nonempty_shape_count(self):
        assert fodp_nonempty_shape_count(_S) == 3

    def test_nonempty_slide_count(self):
        assert fodp_nonempty_slide_count(_S) == 2

    def test_nonempty_slide_ratio(self):
        assert fodp_nonempty_slide_ratio(_S) == 1.0

    def test_note_count(self):
        assert fodp_note_count(_S) == 0

    def test_notes_density(self):
        assert fodp_notes_density(_S) == 0.0

    def test_notes_length_sum(self):
        assert fodp_notes_length_sum(_S) == 0

    def test_notes_text(self):
        notes = fodp_notes_text(_S)
        assert isinstance(notes, list)
        assert len(notes) == 2

    def test_notes_to_slide_ratio(self):
        assert fodp_notes_to_slide_ratio(_S) == 0.0

    def test_notes_total_length(self):
        assert fodp_notes_total_length(_S) == 0

    def test_punctuation_count(self):
        assert fodp_punctuation_count(_S) == 0

    def test_shape_count_variance(self):
        assert fodp_shape_count_variance(_S) == 0.25

    def test_shape_diversity(self):
        assert fodp_shape_diversity(_S) == 2

    def test_shape_to_slide_ratio(self):
        assert fodp_shape_to_slide_ratio(_S) == 1.5

    def test_shape_variance(self):
        assert fodp_shape_variance(_S) == 1

    def test_shortest_slide_index(self):
        assert fodp_shortest_slide_index(_S) == 1

    def test_slide_count(self):
        assert fodp_slide_count(_S) == 2

    def test_slide_shape_counts(self):
        counts = fodp_slide_shape_counts(_S)
        assert counts == [2, 1]

    def test_slide_text_density(self):
        assert fodp_slide_text_density(_S) == 21.5

    def test_slide_text_range(self):
        assert fodp_slide_text_range(_S) == 0

    def test_slide_text_variance(self):
        assert fodp_slide_text_variance(_S) == 121.0

    def test_slide_title_count(self):
        assert fodp_slide_title_count(_S) == 2

    def test_slide_titles(self):
        titles = fodp_slide_titles(_S)
        assert "Introduction" in titles
        assert "Conclusion" in titles

    def test_slide_word_variance(self):
        assert fodp_slide_word_variance(_S) == 0.0

    def test_text_to_slide_ratio(self):
        assert fodp_text_to_slide_ratio(_S) == 21.0

    def test_title_coverage(self):
        assert fodp_title_coverage(_S) == 1.0

    def test_total_chars_per_slide(self):
        assert fodp_total_chars_per_slide(_S) == 21.5

    def test_total_image_count(self):
        assert fodp_total_image_count(_S) == 0

    def test_total_images(self):
        assert fodp_total_images(_S) == 0

    def test_total_notes_length(self):
        assert fodp_total_notes_length(_S) == 0

    def test_total_shape_count(self):
        assert fodp_total_shape_count(_S) == 3

    def test_total_text_chars(self):
        assert fodp_total_text_chars(_S) == 43

    def test_total_text_length(self):
        assert fodp_total_text_length(_S) == 42

    def test_total_title_chars(self):
        assert fodp_total_title_chars(_S) == 22

    def test_unique_slide_title_count(self):
        assert fodp_unique_slide_title_count(_S) == 0

    def test_uppercase_count(self):
        assert fodp_uppercase_count(_S) == 0

    def test_vowel_count(self):
        assert fodp_vowel_count(_S) == 14

    def test_word_count(self):
        assert fodp_word_count(_S) == 5

    def test_word_length_variance(self):
        assert fodp_word_length_variance(_S) == 0.0

    # --- NDJSON roundtrip ---

    def test_ndjson_roundtrip(self, tmp_path):
        out = tmp_path / "fodp_analytics.ndjson"
        records = [
            {"fn": "slide_count", "value": fodp_slide_count(_S)},
            {"fn": "total_shape_count", "value": fodp_total_shape_count(_S)},
            {"fn": "total_text_chars", "value": fodp_total_text_chars(_S)},
            {"fn": "vowel_count", "value": fodp_vowel_count(_S)},
            {"fn": "word_count", "value": fodp_word_count(_S)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 5
        assert loaded[0]["value"] == 2
        assert loaded[1]["value"] == 3
        assert loaded[2]["value"] == 43
        assert loaded[3]["value"] == 14
        assert loaded[4]["value"] == 5
