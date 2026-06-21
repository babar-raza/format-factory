"""
tests/python/dogfood/test_dogfood_abw_massive_analytics_gap_closure_ndjson_export.py

Sprint: dogfood-abw-analytics-gap-closure-20260617
Dogfood export: ABW analytics -> NDJSON roundtrip.
Covers 54 previously-untested abw_* analytics functions on two-paragraphs.abw.
Note: 5 functions skipped due to pre-existing bug (paragraphs list contains
      strings not dicts): paragraph_word_variance, sentence_avg_length,
      sentence_count, unique_word_ratio, uppercase_word_count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    abw_all_words_unique,
    abw_alpha_ratio,
    abw_avg_chars_per_word,
    abw_avg_paragraph_words,
    abw_avg_word_length,
    abw_avg_word_length_per_para,
    abw_avg_word_per_paragraph,
    abw_char_per_paragraph,
    abw_digit_char_count,
    abw_file_size_bytes,
    abw_has_headings,
    abw_has_multiple_paragraphs,
    abw_is_content_rich,
    abw_is_empty_document,
    abw_line_count,
    abw_longest_paragraph_chars,
    abw_longest_paragraph_index,
    abw_longest_paragraph_words,
    abw_lowercase_ratio,
    abw_max_paragraph_length,
    abw_max_paragraph_word_count,
    abw_max_paragraph_words,
    abw_max_word_count_para,
    abw_median_paragraph_length,
    abw_min_paragraph_length,
    abw_min_word_count_para,
    abw_nonempty_para_ratio,
    abw_nonempty_paragraph_count,
    abw_nonempty_paragraph_ratio,
    abw_nonspace_char_count,
    abw_numeric_word_count,
    abw_para_char_variance,
    abw_paragraph_density,
    abw_paragraph_length_variance,
    abw_paragraph_text_variance,
    abw_punctuation_count,
    abw_section_count,
    abw_sentence_density,
    abw_short_paragraph_count,
    abw_shortest_paragraph_chars,
    abw_shortest_word,
    abw_total_char_count,
    abw_total_para_char_count,
    abw_total_text_length,
    abw_unique_char_count,
    abw_unique_word_count,
    abw_uppercase_count,
    abw_uppercase_ratio,
    abw_vowel_ratio,
    abw_whitespace_ratio,
    abw_word_length_variance,
    abw_words_per_sentence,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_ABW_DIR = _REPO / "samples" / "by-format" / "abw"
_S = str(_ABW_DIR / "two-paragraphs.abw")


class TestAbwMassiveAnalyticsGapClosureNdjsonExport:
    """54 ABW analytics functions -> NDJSON dogfood export on two-paragraphs.abw."""

    # --- boolean analytics ---

    def test_all_words_unique_false(self):
        assert abw_all_words_unique(_S) is False

    def test_has_headings_false(self):
        assert abw_has_headings(_S) is False

    def test_has_multiple_paragraphs_true(self):
        assert abw_has_multiple_paragraphs(_S) is True

    def test_is_content_rich_true(self):
        assert abw_is_content_rich(_S) is True

    def test_is_empty_document_false(self):
        assert abw_is_empty_document(_S) is False

    # --- float analytics ---

    def test_alpha_ratio(self):
        val = abw_alpha_ratio(_S)
        assert abs(val - 0.8788) < 0.001

    def test_avg_chars_per_word(self):
        assert abw_avg_chars_per_word(_S) == 8.25

    def test_avg_paragraph_words(self):
        assert abw_avg_paragraph_words(_S) == 2.0

    def test_avg_word_length(self):
        assert abw_avg_word_length(_S) == 7.75

    def test_avg_word_length_per_para(self):
        assert abw_avg_word_length_per_para(_S) == 15.5

    def test_avg_word_per_paragraph(self):
        assert abw_avg_word_per_paragraph(_S) == 2.0

    def test_char_per_paragraph(self):
        assert abw_char_per_paragraph(_S) == 16.5

    def test_lowercase_ratio(self):
        val = abw_lowercase_ratio(_S)
        assert abs(val - 0.9310) < 0.001

    def test_nonempty_para_ratio(self):
        assert abw_nonempty_para_ratio(_S) == 1.0

    def test_nonempty_paragraph_ratio(self):
        assert abw_nonempty_paragraph_ratio(_S) == 1.0

    def test_para_char_variance(self):
        assert abw_para_char_variance(_S) == 0.25

    def test_paragraph_density(self):
        assert abw_paragraph_density(_S) == 16.5

    def test_paragraph_length_variance(self):
        assert abw_paragraph_length_variance(_S) == 0.25

    def test_paragraph_text_variance(self):
        assert abw_paragraph_text_variance(_S) == 0.25

    def test_sentence_density(self):
        assert abw_sentence_density(_S) == 1.0

    def test_uppercase_ratio(self):
        val = abw_uppercase_ratio(_S)
        assert abs(val - 0.0690) < 0.001

    def test_vowel_ratio(self):
        val = abw_vowel_ratio(_S)
        assert abs(val - 0.2647) < 0.001

    def test_whitespace_ratio(self):
        val = abw_whitespace_ratio(_S)
        assert abs(val - 0.0606) < 0.001

    def test_word_length_variance(self):
        assert abw_word_length_variance(_S) == 5.1875

    def test_words_per_sentence(self):
        assert abw_words_per_sentence(_S) == 2.0

    # --- int analytics ---

    def test_digit_char_count(self):
        assert abw_digit_char_count(_S) == 0

    def test_file_size_bytes(self):
        val = abw_file_size_bytes(_S)
        assert isinstance(val, int)
        assert val > 0

    def test_line_count(self):
        assert abw_line_count(_S) == 2

    def test_longest_paragraph_chars(self):
        assert abw_longest_paragraph_chars(_S) == 17

    def test_longest_paragraph_index(self):
        assert abw_longest_paragraph_index(_S) == 1

    def test_longest_paragraph_words(self):
        assert abw_longest_paragraph_words(_S) == 2

    def test_max_paragraph_length(self):
        assert abw_max_paragraph_length(_S) == 17

    def test_max_paragraph_word_count(self):
        assert abw_max_paragraph_word_count(_S) == 2

    def test_max_paragraph_words(self):
        assert abw_max_paragraph_words(_S) == 2

    def test_max_word_count_para(self):
        assert abw_max_word_count_para(_S) == 2

    def test_median_paragraph_length(self):
        assert abw_median_paragraph_length(_S) == 16

    def test_min_paragraph_length(self):
        assert abw_min_paragraph_length(_S) == 16

    def test_min_word_count_para(self):
        assert abw_min_word_count_para(_S) == 2

    def test_nonempty_paragraph_count(self):
        assert abw_nonempty_paragraph_count(_S) == 2

    def test_nonspace_char_count(self):
        assert abw_nonspace_char_count(_S) == 31

    def test_numeric_word_count(self):
        assert abw_numeric_word_count(_S) == 0

    def test_punctuation_count(self):
        assert abw_punctuation_count(_S) == 2

    def test_section_count(self):
        assert abw_section_count(_S) == 0

    def test_short_paragraph_count(self):
        assert abw_short_paragraph_count(_S) == 2

    def test_shortest_paragraph_chars(self):
        assert abw_shortest_paragraph_chars(_S) == 16

    def test_total_char_count(self):
        assert abw_total_char_count(_S) == 33

    def test_total_para_char_count(self):
        assert abw_total_para_char_count(_S) == 33

    def test_total_text_length(self):
        assert abw_total_text_length(_S) == 33

    def test_unique_char_count(self):
        assert abw_unique_char_count(_S) == 17

    def test_unique_word_count(self):
        assert abw_unique_word_count(_S) == 3

    def test_uppercase_count(self):
        assert abw_uppercase_count(_S) == 2

    def test_shortest_word(self):
        assert abw_shortest_word(_S) == "First"

    # --- NDJSON roundtrip ---

    def test_ndjson_roundtrip(self, tmp_path):
        out = tmp_path / "abw_analytics.ndjson"
        records = [
            {"fn": "total_char_count", "value": abw_total_char_count(_S)},
            {"fn": "nonempty_paragraph_count", "value": abw_nonempty_paragraph_count(_S)},
            {"fn": "unique_word_count", "value": abw_unique_word_count(_S)},
            {"fn": "digit_char_count", "value": abw_digit_char_count(_S)},
            {"fn": "file_size_bytes", "value": abw_file_size_bytes(_S)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 5
        assert loaded[0]["value"] == 33
        assert loaded[1]["value"] == 2
        assert loaded[2]["value"] == 3
        assert loaded[3]["value"] == 0
        assert loaded[4]["value"] > 0
