"""Tests for abw_min_paragraph_length, abw_has_content, abw_heading_count,
abw_vocabulary_richness, abw_average_paragraph_length (Sprint 39).

Closes:
  GAP-ABW-FOSS-ABW_MIN_PARA-001  (Abw Min Paragraph Length)
  GAP-ABW-FOSS-ABW_HAS_CONT-001  (Abw Has Content)
  GAP-ABW-FOSS-ABW_HEADING_-001  (Abw Heading Count)
  GAP-ABW-FOSS-ABW_VOCABULA-001  (Abw Vocabulary Richness)
  GAP-ABW-FOSS-ABW_AVERAGE_-001  (Abw Average Paragraph Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    abw_average_paragraph_length,
    abw_has_content,
    abw_heading_count,
    abw_min_paragraph_length,
    abw_vocabulary_richness,
)

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")       # "Hello" — 1 para, 5 chars
_TWO_PARA = str(_DIR / "two-paragraphs.abw")        # 2 paras: "First paragraph."(16) + "Second paragraph."(17)
_EMPTY_SEC = str(_DIR / "empty-section.abw")        # empty — no content


class TestAbwMinParagraphLength:
    def test_return_type(self):
        assert isinstance(abw_min_paragraph_length(_MINIMAL), int)

    def test_exact_5_for_minimal(self):
        # minimal-document.abw: "Hello" = 5 chars, only 1 para -> min=5
        assert abw_min_paragraph_length(_MINIMAL) == 5

    def test_exact_16_for_two_para(self):
        # two-paragraphs.abw: "First paragraph."(16), "Second paragraph."(17) -> min=16
        assert abw_min_paragraph_length(_TWO_PARA) == 16

    def test_zero_for_empty(self):
        # empty-section.abw: no paragraphs -> min=0
        assert abw_min_paragraph_length(_EMPTY_SEC) == 0

    def test_nonnegative(self):
        assert abw_min_paragraph_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_min_paragraph_length(_MINIMAL) == abw_min_paragraph_length(_MINIMAL)


class TestAbwHasContent:
    def test_return_type(self):
        assert isinstance(abw_has_content(_MINIMAL), bool)

    def test_true_for_minimal(self):
        # minimal-document.abw has "Hello"
        assert abw_has_content(_MINIMAL) is True

    def test_true_for_two_para(self):
        assert abw_has_content(_TWO_PARA) is True

    def test_false_for_empty(self):
        # empty-section.abw has no text content
        assert abw_has_content(_EMPTY_SEC) is False

    def test_consistent_across_calls(self):
        assert abw_has_content(_MINIMAL) == abw_has_content(_MINIMAL)


class TestAbwHeadingCount:
    def test_return_type(self):
        assert isinstance(abw_heading_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        # minimal-document.abw: plain text, no headings
        assert abw_heading_count(_MINIMAL) == 0

    def test_zero_for_two_para(self):
        # two-paragraphs.abw: body paragraphs, no headings
        assert abw_heading_count(_TWO_PARA) == 0

    def test_zero_for_empty(self):
        assert abw_heading_count(_EMPTY_SEC) == 0

    def test_nonnegative(self):
        assert abw_heading_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_heading_count(_MINIMAL) == abw_heading_count(_MINIMAL)


class TestAbwVocabularyRichness:
    def test_return_type(self):
        assert isinstance(abw_vocabulary_richness(_MINIMAL), float)

    def test_exact_1_0_for_minimal(self):
        # "Hello": 1 unique word / 1 total = 1.0
        assert abw_vocabulary_richness(_MINIMAL) == 1.0

    def test_exact_0_75_for_two_para(self):
        # two-paragraphs: "First paragraph. Second paragraph."
        # words: First, paragraph, Second, paragraph -> 3 unique / 4 total = 0.75
        assert abw_vocabulary_richness(_TWO_PARA) == 0.75

    def test_zero_for_empty(self):
        assert abw_vocabulary_richness(_EMPTY_SEC) == 0.0

    def test_range_0_to_1(self):
        r = abw_vocabulary_richness(_TWO_PARA)
        assert 0.0 <= r <= 1.0

    def test_consistent_across_calls(self):
        assert abw_vocabulary_richness(_MINIMAL) == abw_vocabulary_richness(_MINIMAL)


class TestAbwAverageParagraphLength:
    def test_return_type(self):
        assert isinstance(abw_average_paragraph_length(_MINIMAL), float)

    def test_exact_5_0_for_minimal(self):
        # "Hello" = 5 chars, 1 paragraph -> avg=5.0
        assert abw_average_paragraph_length(_MINIMAL) == 5.0

    def test_exact_16_5_for_two_para(self):
        # "First paragraph."(16) + "Second paragraph."(17) -> avg=(16+17)/2=16.5
        assert abw_average_paragraph_length(_TWO_PARA) == 16.5

    def test_zero_for_empty(self):
        assert abw_average_paragraph_length(_EMPTY_SEC) == 0.0

    def test_nonnegative(self):
        assert abw_average_paragraph_length(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert abw_average_paragraph_length(_MINIMAL) == abw_average_paragraph_length(_MINIMAL)
