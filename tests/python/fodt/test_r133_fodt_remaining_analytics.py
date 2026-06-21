"""
test_r133_fodt_remaining_analytics.py — Test coverage for remaining FODT analytics gaps.

Gaps closed (17 total):
- GAP-FODT-FOSS-FODT_FILE_SI-001  (fodt_file_size_bytes)
- GAP-FODT-FOSS-FODT_HAS_MOR-001  (fodt_has_more_words_than_unique)
- GAP-FODT-FOSS-FODT_UPPERCA-001  (fodt_uppercase_char_count)
- GAP-FODT-FOSS-FODT_MIN_HEA-001  (fodt_min_heading_length)
- GAP-FODT-FOSS-FODT_CHAR_PE-001  (fodt_char_per_word)
- GAP-FODT-FOSS-FODT_AVG_BLO-001  (fodt_avg_block_length)
- GAP-FODT-FOSS-FODT_MAX_BLO-001  (fodt_max_block_text_length)
- GAP-FODT-FOSS-FODT_MIN_BLO-001  (fodt_min_block_text_length)
- GAP-FODT-FOSS-FODT_WORD_PE-001  (fodt_word_per_heading)
- GAP-FODT-FOSS-FODT_BLOCK_T-001  (fodt_block_text_sum)
- GAP-FODT-FOSS-FODT_CONSONA-001  (fodt_consonant_ratio)
- GAP-FODT-FOSS-FODT_AVG_RUN-001  (fodt_avg_run_count)
- GAP-FODT-FOSS-FODT_EMPTY_B-001  (fodt_empty_block_count)
- GAP-FODT-FOSS-FODT_WORD_DE-001  (fodt_word_density)
- GAP-FODT-FOSS-FODT_AVG_PAR-001  (fodt_avg_paragraph_length)
- GAP-FODT-FOSS-FODT_SECTION-001  (fodt_section_depth_max)
- GAP-FODT-FOSS-FODT_TEXT_BL-001  (fodt_text_block_ratio)
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.fodt_analytics import (
    fodt_file_size_bytes,
    fodt_has_more_words_than_unique,
    fodt_uppercase_char_count,
    fodt_min_heading_length,
    fodt_char_per_word,
    fodt_avg_block_length,
    fodt_max_block_text_length,
    fodt_min_block_text_length,
    fodt_word_per_heading,
    fodt_block_text_sum,
    fodt_consonant_ratio,
    fodt_avg_run_count,
    fodt_empty_block_count,
    fodt_word_density,
    fodt_avg_paragraph_length,
    fodt_section_depth_max,
    fodt_text_block_ratio,
)


class TestFodtFileSizeBytes:
    """GAP-FODT-FOSS-FODT_FILE_SI-001."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_file_size_bytes(f), int)

    def test_positive(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_file_size_bytes(f) > 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_file_size_bytes(sample)
            assert isinstance(result, int) and result > 0, f"Failed for {sample}"


class TestFodtHasMoreWordsThanUnique:
    """GAP-FODT-FOSS-FODT_HAS_MOR-001."""

    def test_returns_bool(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_has_more_words_than_unique(f), bool)

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_has_more_words_than_unique(sample)
            assert isinstance(result, bool), f"Failed for {sample}"


class TestFodtUppercaseCharCount:
    """GAP-FODT-FOSS-FODT_UPPERCA-001."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_uppercase_char_count(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_uppercase_char_count(f) >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_uppercase_char_count(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtMinHeadingLength:
    """GAP-FODT-FOSS-FODT_MIN_HEA-001."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_min_heading_length(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_min_heading_length(f) >= 0

    def test_minimal_document(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_min_heading_length(f)
        assert isinstance(result, int) and result >= 0


class TestFodtCharPerWord:
    """GAP-FODT-FOSS-FODT_CHAR_PE-001."""

    def test_returns_float(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_char_per_word(f), float)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_char_per_word(f) >= 0.0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_char_per_word(sample)
            assert isinstance(result, (int, float)) and result >= 0, f"Failed for {sample}"


class TestFodtAvgBlockLength:
    """GAP-FODT-FOSS-FODT_AVG_BLO-001."""

    def test_returns_float(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_avg_block_length(f), float)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_avg_block_length(f) >= 0.0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_avg_block_length(sample)
            assert isinstance(result, (int, float)) and result >= 0, f"Failed for {sample}"


class TestFodtMaxBlockTextLength:
    """GAP-FODT-FOSS-FODT_MAX_BLO-001."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_max_block_text_length(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_max_block_text_length(f) >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_max_block_text_length(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtMinBlockTextLength:
    """GAP-FODT-FOSS-FODT_MIN_BLO-001."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_min_block_text_length(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_min_block_text_length(f) >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_min_block_text_length(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtWordPerHeading:
    """GAP-FODT-FOSS-FODT_WORD_PE-001."""

    def test_returns_float(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_word_per_heading(f), float)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_word_per_heading(f) >= 0.0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_word_per_heading(sample)
            assert isinstance(result, (int, float)) and result >= 0, f"Failed for {sample}"


class TestFodtBlockTextSum:
    """GAP-FODT-FOSS-FODT_BLOCK_T-001."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_block_text_sum(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_block_text_sum(f) >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_block_text_sum(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtConsonantRatio:
    """GAP-FODT-FOSS-FODT_CONSONA-001."""

    def test_returns_float(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_consonant_ratio(f), float)

    def test_between_zero_and_one(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        result = fodt_consonant_ratio(f)
        assert 0.0 <= result <= 1.0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_consonant_ratio(sample)
            assert isinstance(result, (int, float)) and 0.0 <= result <= 1.0, f"Failed for {sample}"


class TestFodtAvgRunCount:
    """GAP-FODT-FOSS-FODT_AVG_RUN-001."""

    def test_returns_float(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_avg_run_count(f), float)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_avg_run_count(f) >= 0.0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_avg_run_count(sample)
            assert isinstance(result, (int, float)) and result >= 0, f"Failed for {sample}"


class TestFodtEmptyBlockCount:
    """GAP-FODT-FOSS-FODT_EMPTY_B-001."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_empty_block_count(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_empty_block_count(f) >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_empty_block_count(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtWordDensity:
    """GAP-FODT-FOSS-FODT_WORD_DE-001."""

    def test_returns_float(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_word_density(f), float)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_word_density(f) >= 0.0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_word_density(sample)
            assert isinstance(result, (int, float)) and result >= 0, f"Failed for {sample}"


class TestFodtAvgParagraphLength:
    """GAP-FODT-FOSS-FODT_AVG_PAR-001."""

    def test_returns_float(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_avg_paragraph_length(f), float)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_avg_paragraph_length(f) >= 0.0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_avg_paragraph_length(sample)
            assert isinstance(result, (int, float)) and result >= 0, f"Failed for {sample}"


class TestFodtSectionDepthMax:
    """GAP-FODT-FOSS-FODT_SECTION-001."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_section_depth_max(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_section_depth_max(f) >= 0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_section_depth_max(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"


class TestFodtTextBlockRatio:
    """GAP-FODT-FOSS-FODT_TEXT_BL-001."""

    def test_returns_float(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_text_block_ratio(f), float)

    def test_between_zero_and_one(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        result = fodt_text_block_ratio(f)
        assert 0.0 <= result <= 1.0

    def test_all_samples(self):
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_text_block_ratio(sample)
            assert isinstance(result, (int, float)) and 0.0 <= result <= 1.0, f"Failed for {sample}"
