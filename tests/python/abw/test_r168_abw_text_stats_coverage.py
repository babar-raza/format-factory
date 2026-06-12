"""
test_r168_abw_text_stats_coverage.py

Sprint: FORMAT-FACTORY-HARDENED-AUDIT-REMEDIATION-SPRINT9-001
Added: 2026-06-11

Tests for ABW text analysis functions: get_metadata, extract_text, text_stats,
get_char_count, word_frequency, get_unique_words, paragraph_lengths, contains_text.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import (
    load,
    probe_abw,
    get_metadata,
    extract_text,
    text_stats,
    get_char_count,
    word_frequency,
    get_unique_words,
    paragraph_lengths,
    contains_text,
    create_abw,
    write_abw,
    AbwError,
    AbwParseError,
)

_SAMPLES = _REPO / "samples" / "by-format" / "abw"
_TWO_PARA = _SAMPLES / "two-paragraphs.abw"
_MINIMAL = _SAMPLES / "minimal-document.abw"


def _make_abw(paragraphs, tmp_path):
    doc = create_abw(paragraphs)
    p = tmp_path / "test.abw"
    write_abw(doc, str(p))
    return p


# ── probe_abw ─────────────────────────────────────────────────────────────

class TestProbeAbw:

    def test_returns_bool(self):
        assert isinstance(probe_abw(_TWO_PARA), bool)

    def test_valid_file_true(self):
        assert probe_abw(_TWO_PARA) is True

    def test_nonexistent_false(self, tmp_path):
        assert probe_abw(tmp_path / "no_such.abw") is False


# ── get_metadata ──────────────────────────────────────────────────────────

class TestGetMetadata:

    def test_returns_dict(self):
        result = get_metadata(_TWO_PARA)
        assert isinstance(result, dict)

    def test_from_minimal(self):
        result = get_metadata(_MINIMAL)
        assert isinstance(result, dict)

    def test_from_tmp_file(self, tmp_path):
        p = _make_abw(["Hello world"], tmp_path)
        result = get_metadata(p)
        assert isinstance(result, dict)


# ── extract_text ──────────────────────────────────────────────────────────

class TestExtractText:

    def test_returns_list(self):
        result = extract_text(_TWO_PARA)
        assert isinstance(result, list)

    def test_has_content(self):
        result = extract_text(_TWO_PARA)
        assert len(result) >= 1

    def test_strings_in_list(self):
        result = extract_text(_TWO_PARA)
        for item in result:
            assert isinstance(item, str)

    def test_two_paragraphs_count(self):
        result = extract_text(_TWO_PARA)
        assert len(result) == 2


# ── text_stats ────────────────────────────────────────────────────────────

class TestTextStats:

    def test_returns_dict(self):
        model = load(_TWO_PARA)
        result = text_stats(model)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        model = load(_TWO_PARA)
        result = text_stats(model)
        assert "paragraph_count" in result
        assert "word_count" in result
        assert "char_count" in result

    def test_paragraph_count_matches(self):
        model = load(_TWO_PARA)
        result = text_stats(model)
        assert result["paragraph_count"] == 2

    def test_word_count_positive(self):
        model = load(_TWO_PARA)
        result = text_stats(model)
        assert result["word_count"] > 0


# ── get_char_count ────────────────────────────────────────────────────────

class TestGetCharCount:

    def test_returns_int(self):
        model = load(_TWO_PARA)
        assert isinstance(get_char_count(model), int)

    def test_positive(self):
        model = load(_TWO_PARA)
        assert get_char_count(model) > 0

    def test_from_synthetic(self, tmp_path):
        p = _make_abw(["hello"], tmp_path)
        model = load(p)
        assert get_char_count(model) == 5


# ── word_frequency ────────────────────────────────────────────────────────

class TestWordFrequency:

    def test_returns_dict(self):
        model = load(_TWO_PARA)
        result = word_frequency(model)
        assert isinstance(result, dict)

    def test_values_are_ints(self):
        model = load(_TWO_PARA)
        result = word_frequency(model)
        for v in result.values():
            assert isinstance(v, int)

    def test_repeated_word_counted(self, tmp_path):
        p = _make_abw(["apple apple", "apple"], tmp_path)
        model = load(p)
        freq = word_frequency(model)
        assert freq.get("apple", 0) == 3


# ── get_unique_words ──────────────────────────────────────────────────────

class TestGetUniqueWords:

    def test_returns_list(self):
        model = load(_TWO_PARA)
        result = get_unique_words(model)
        assert isinstance(result, list)

    def test_no_duplicates(self, tmp_path):
        p = _make_abw(["hello hello world"], tmp_path)
        model = load(p)
        result = get_unique_words(model)
        assert len(result) == len(set(result))


# ── paragraph_lengths ─────────────────────────────────────────────────────

class TestParagraphLengths:

    def test_returns_list(self):
        model = load(_TWO_PARA)
        result = paragraph_lengths(model)
        assert isinstance(result, list)

    def test_count_matches_paragraphs(self):
        model = load(_TWO_PARA)
        result = paragraph_lengths(model)
        assert len(result) == 2

    def test_lengths_are_ints(self):
        model = load(_TWO_PARA)
        result = paragraph_lengths(model)
        for n in result:
            assert isinstance(n, int)


# ── contains_text ─────────────────────────────────────────────────────────

class TestContainsText:

    def test_returns_bool(self):
        model = load(_TWO_PARA)
        assert isinstance(contains_text(model, "paragraph"), bool)

    def test_existing_text_true(self):
        model = load(_TWO_PARA)
        assert contains_text(model, "First") is True

    def test_missing_text_false(self):
        model = load(_TWO_PARA)
        assert contains_text(model, "NoSuchTextXXXYYY") is False

    def test_case_insensitive(self):
        model = load(_TWO_PARA)
        assert contains_text(model, "first", case_sensitive=False) is True
