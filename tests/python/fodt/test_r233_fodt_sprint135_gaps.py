"""Tests for FODT Sprint 135 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_VOWEL_C-001   (Fodt Vowel Count)
  GAP-FODT-FOSS-FODT_SPACE_C-001   (Fodt Space Count)
  GAP-FODT-FOSS-FODT_NUMERIC-001   (Fodt Numeric Word Count)
  GAP-FODT-FOSS-FODT_MAX_WOR-001   (Fodt Max Words In Heading)
  GAP-FODT-FOSS-FODT_SHORT_P-001   (Fodt Short Paragraph Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import (
    fodt_vowel_count, fodt_space_count, fodt_numeric_word_count,
    fodt_max_words_in_heading, fodt_short_paragraph_count,
)

_DIR = _REPO / "samples" / "by-format" / "fodt"
_HEAD = str(_DIR / "headings-and-paragraphs.fodt")
_MINIMAL = str(_DIR / "minimal-document.fodt")
_LIST = str(_DIR / "list-basic.fodt")


class TestFodtVowelCount:
    def test_return_type(self):
        assert isinstance(fodt_vowel_count(_HEAD), int)

    def test_exact_88_for_headings(self):
        assert fodt_vowel_count(_HEAD) == 88

    def test_exact_3_for_minimal(self):
        assert fodt_vowel_count(_MINIMAL) == 3

    def test_exact_13_for_list(self):
        assert fodt_vowel_count(_LIST) == 13

    def test_nonnegative(self):
        assert fodt_vowel_count(_MINIMAL) >= 0

    def test_consistent(self):
        assert fodt_vowel_count(_HEAD) == fodt_vowel_count(_HEAD)


class TestFodtSpaceCount:
    def test_return_type(self):
        assert isinstance(fodt_space_count(_HEAD), int)

    def test_exact_37_for_headings(self):
        assert fodt_space_count(_HEAD) == 37

    def test_exact_1_for_minimal(self):
        assert fodt_space_count(_MINIMAL) == 1

    def test_exact_4_for_list(self):
        assert fodt_space_count(_LIST) == 4

    def test_nonnegative(self):
        assert fodt_space_count(_MINIMAL) >= 0

    def test_consistent(self):
        assert fodt_space_count(_HEAD) == fodt_space_count(_HEAD)


class TestFodtNumericWordCount:
    def test_return_type(self):
        assert isinstance(fodt_numeric_word_count(_HEAD), int)

    def test_exact_0_for_headings(self):
        assert fodt_numeric_word_count(_HEAD) == 0

    def test_exact_0_for_minimal(self):
        assert fodt_numeric_word_count(_MINIMAL) == 0

    def test_nonnegative(self):
        assert fodt_numeric_word_count(_MINIMAL) >= 0

    def test_consistent(self):
        assert fodt_numeric_word_count(_HEAD) == fodt_numeric_word_count(_HEAD)


class TestFodtMaxWordsInHeading:
    def test_return_type(self):
        assert isinstance(fodt_max_words_in_heading(_HEAD), int)

    def test_exact_3_for_headings(self):
        assert fodt_max_words_in_heading(_HEAD) == 3

    def test_exact_0_for_minimal(self):
        assert fodt_max_words_in_heading(_MINIMAL) == 0

    def test_nonnegative(self):
        assert fodt_max_words_in_heading(_MINIMAL) >= 0

    def test_consistent(self):
        assert fodt_max_words_in_heading(_HEAD) == fodt_max_words_in_heading(_HEAD)


class TestFodtShortParagraphCount:
    def test_return_type(self):
        assert isinstance(fodt_short_paragraph_count(_HEAD), int)

    def test_exact_2_for_headings(self):
        assert fodt_short_paragraph_count(_HEAD) == 2

    def test_exact_1_for_minimal(self):
        assert fodt_short_paragraph_count(_MINIMAL) == 1

    def test_exact_2_for_list(self):
        assert fodt_short_paragraph_count(_LIST) == 2

    def test_nonnegative(self):
        assert fodt_short_paragraph_count(_MINIMAL) >= 0

    def test_consistent(self):
        assert fodt_short_paragraph_count(_HEAD) == fodt_short_paragraph_count(_HEAD)
