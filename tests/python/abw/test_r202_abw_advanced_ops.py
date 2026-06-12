"""
tests/python/abw/test_r202_abw_advanced_ops.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-SPRINT15-001
TASK-001 (part B): ABW advanced operations.

Covers: probe_abw, load, extract_text, get_paragraph_count, get_word_count,
text_stats, abw_sentence_count, abw_total_char_count, contains_text,
get_unique_words, paragraph_lengths, first_paragraph, last_paragraph,
is_empty, average_paragraph_length, get_words, abw_empty_paragraph_count,
abw_nonempty_paragraph_count, get_metadata.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    probe_abw, load, extract_text, get_paragraph_count, get_word_count,
    text_stats, abw_sentence_count, abw_total_char_count, contains_text,
    get_unique_words, paragraph_lengths, first_paragraph, last_paragraph,
    is_empty, average_paragraph_length, get_words, abw_empty_paragraph_count,
    abw_nonempty_paragraph_count, get_metadata,
)

_SAMPLES = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_SAMPLES / "minimal-document.abw")
_TWO = str(_SAMPLES / "two-paragraphs.abw")


class TestAbwProbeAndLoad:
    """probe_abw, load, extract_text, get_paragraph_count, get_metadata."""

    def test_probe_abw_true(self):
        # probe_abw returns True/False (bool), not dict
        assert probe_abw(_MINIMAL) is True

    def test_probe_abw_two_paragraphs(self):
        assert probe_abw(_TWO) is True

    def test_load_returns_dict(self):
        model = load(_MINIMAL)
        assert isinstance(model, dict)

    def test_extract_text_list(self):
        texts = extract_text(_TWO)
        assert isinstance(texts, list)
        assert len(texts) == 2

    def test_extract_text_strings(self):
        texts = extract_text(_TWO)
        assert all(isinstance(t, str) for t in texts)

    def test_get_paragraph_count_int(self):
        count = get_paragraph_count(_TWO)
        assert isinstance(count, int)
        assert count == 2

    def test_get_paragraph_count_minimal(self):
        count = get_paragraph_count(_MINIMAL)
        assert isinstance(count, int)
        assert count >= 1

    def test_abw_empty_paragraph_count_int(self):
        n = abw_empty_paragraph_count(_TWO)
        assert isinstance(n, int)
        assert n == 0

    def test_abw_nonempty_paragraph_count_int(self):
        n = abw_nonempty_paragraph_count(_TWO)
        assert isinstance(n, int)
        assert n == 2

    def test_get_metadata_dict(self):
        meta = get_metadata(_MINIMAL)
        assert isinstance(meta, dict)


class TestAbwTextAnalytics:
    """get_word_count, text_stats, abw_sentence_count, abw_total_char_count — take model dict."""

    def test_get_word_count_int(self):
        model = load(_TWO)
        count = get_word_count(model)
        assert isinstance(count, int)
        assert count >= 1

    def test_text_stats_dict(self):
        model = load(_TWO)
        stats = text_stats(model)
        assert isinstance(stats, dict)
        assert "word_count" in stats

    def test_text_stats_paragraph_count(self):
        model = load(_TWO)
        stats = text_stats(model)
        assert stats.get("paragraph_count") == 2

    def test_abw_sentence_count_int(self):
        model = load(_TWO)
        n = abw_sentence_count(model)
        assert isinstance(n, int)
        assert n >= 1

    def test_abw_total_char_count_int(self):
        # abw_total_char_count takes path
        n = abw_total_char_count(_TWO)
        assert isinstance(n, int)
        assert n > 0

    def test_contains_text_true(self):
        model = load(_TWO)
        assert contains_text(model, "paragraph") is True

    def test_contains_text_false(self):
        model = load(_TWO)
        assert contains_text(model, "xyz_not_found_999") is False


class TestAbwWordOps:
    """get_unique_words, get_words, paragraph_lengths — take model dict."""

    def test_get_unique_words_list(self):
        model = load(_TWO)
        words = get_unique_words(model)
        assert isinstance(words, list)
        assert len(words) >= 1

    def test_get_words_list(self):
        # get_words(model, para_idx) → list[str]
        model = load(_TWO)
        words = get_words(model, 0)
        assert isinstance(words, list)
        assert len(words) >= 1

    def test_paragraph_lengths_list(self):
        model = load(_TWO)
        lengths = paragraph_lengths(model)
        assert isinstance(lengths, list)
        assert len(lengths) == 2

    def test_paragraph_lengths_ints(self):
        model = load(_TWO)
        lengths = paragraph_lengths(model)
        assert all(isinstance(n, int) for n in lengths)

    def test_first_paragraph_str(self):
        model = load(_TWO)
        fp = first_paragraph(model)
        assert isinstance(fp, str)
        assert len(fp) > 0

    def test_last_paragraph_str(self):
        model = load(_TWO)
        lp = last_paragraph(model)
        assert isinstance(lp, str)
        assert len(lp) > 0

    def test_is_empty_false(self):
        model = load(_TWO)
        assert is_empty(model) is False

    def test_average_paragraph_length_float(self):
        model = load(_TWO)
        avg = average_paragraph_length(model)
        assert isinstance(avg, (int, float))
        assert avg > 0
