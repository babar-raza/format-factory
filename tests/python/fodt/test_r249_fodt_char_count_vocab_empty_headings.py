"""Tests for fodt_char_count, fodt_vocabulary_richness, fodt_is_empty, fodt_has_headings (Sprint 39).

Closes:
  GAP-FODT-FOSS-FODT_CHAR_CO-001  (Fodt Char Count)
  GAP-FODT-FOSS-FODT_VOCABUL-001  (Fodt Vocabulary Richness)
  GAP-FODT-FOSS-FODT_IS_EMPT-001  (Fodt Is Empty)
  GAP-FODT-FOSS-FODT_HAS_HEA-001  (Fodt Has Headings)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import (
    fodt_char_count,
    fodt_has_headings,
    fodt_is_empty,
    fodt_vocabulary_richness,
)

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")              # "Hello, world." (13 chars)
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")      # 3 headings, 237 chars
_LIST = str(_DIR / "list-basic.fodt")                       # 42 chars, no headings
_TABLE = str(_DIR / "table-basic.fodt")                     # 41 chars, no headings


class TestFodtCharCount:
    def test_return_type(self):
        assert isinstance(fodt_char_count(_MINIMAL), int)

    def test_exact_13_for_minimal(self):
        # minimal-document.fodt: "Hello, world." = 13 chars
        assert fodt_char_count(_MINIMAL) == 13

    def test_exact_237_for_headings(self):
        # headings-and-paragraphs.fodt: 237 chars total
        assert fodt_char_count(_HEADINGS) == 237

    def test_exact_42_for_list(self):
        # list-basic.fodt: 42 chars
        assert fodt_char_count(_LIST) == 42

    def test_exact_41_for_table(self):
        # table-basic.fodt: 41 chars
        assert fodt_char_count(_TABLE) == 41

    def test_nonnegative(self):
        assert fodt_char_count(_MINIMAL) >= 0

    def test_headings_has_more_chars_than_minimal(self):
        assert fodt_char_count(_HEADINGS) > fodt_char_count(_MINIMAL)

    def test_consistent_across_calls(self):
        assert fodt_char_count(_MINIMAL) == fodt_char_count(_MINIMAL)


class TestFodtVocabularyRichness:
    def test_return_type(self):
        assert isinstance(fodt_vocabulary_richness(_MINIMAL), float)

    def test_exact_1_0_for_minimal(self):
        # minimal-document.fodt: all unique words -> richness=1.0
        assert fodt_vocabulary_richness(_MINIMAL) == 1.0

    def test_less_than_1_for_headings(self):
        # headings-and-paragraphs.fodt: repeated words -> richness < 1.0
        r = fodt_vocabulary_richness(_HEADINGS)
        assert r < 1.0

    def test_headings_richness_approx(self):
        # Approx 0.567 based on probe
        r = fodt_vocabulary_richness(_HEADINGS)
        assert 0.4 <= r <= 0.7

    def test_range_0_to_1(self):
        r = fodt_vocabulary_richness(_MINIMAL)
        assert 0.0 <= r <= 1.0

    def test_list_richness_in_range(self):
        r = fodt_vocabulary_richness(_LIST)
        assert 0.5 <= r <= 0.8

    def test_consistent_across_calls(self):
        assert fodt_vocabulary_richness(_MINIMAL) == fodt_vocabulary_richness(_MINIMAL)


class TestFodtIsEmpty:
    def test_return_type(self):
        assert isinstance(fodt_is_empty(_MINIMAL), bool)

    def test_false_for_minimal(self):
        # minimal-document.fodt has text -> not empty
        assert fodt_is_empty(_MINIMAL) is False

    def test_false_for_headings(self):
        assert fodt_is_empty(_HEADINGS) is False

    def test_false_for_list(self):
        assert fodt_is_empty(_LIST) is False

    def test_false_for_table(self):
        assert fodt_is_empty(_TABLE) is False

    def test_consistent_across_calls(self):
        assert fodt_is_empty(_MINIMAL) == fodt_is_empty(_MINIMAL)


class TestFodtHasHeadings:
    def test_return_type(self):
        assert isinstance(fodt_has_headings(_MINIMAL), bool)

    def test_false_for_minimal(self):
        # minimal-document.fodt: plain paragraph, no headings
        assert fodt_has_headings(_MINIMAL) is False

    def test_true_for_headings_doc(self):
        # headings-and-paragraphs.fodt: 3 headings
        assert fodt_has_headings(_HEADINGS) is True

    def test_false_for_list(self):
        # list-basic.fodt: lists only, no headings
        assert fodt_has_headings(_LIST) is False

    def test_false_for_table(self):
        # table-basic.fodt: table only, no headings
        assert fodt_has_headings(_TABLE) is False

    def test_consistent_across_calls(self):
        assert fodt_has_headings(_MINIMAL) == fodt_has_headings(_MINIMAL)
