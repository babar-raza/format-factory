"""Tests for ABW Sprint 45 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_CHAR_PER-001  (Abw Char Per Paragraph)
  GAP-ABW-FOSS-ABW_IS_EMPTY-001  (Abw Is Empty Document)
  GAP-ABW-FOSS-ABW_FILE_SIZ-001  (Abw File Size Bytes)
  GAP-ABW-FOSS-ABW_MAX_WORD-001  (Abw Max Word Count Para)
  GAP-ABW-FOSS-ABW_MIN_WORD-001  (Abw Min Word Count Para)
  GAP-ABW-FOSS-ABW_DIGIT_CH-001  (Abw Digit Char Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    abw_char_per_paragraph,
    abw_is_empty_document,
    abw_file_size_bytes,
    abw_max_word_count_para,
    abw_min_word_count_para,
    abw_digit_char_count,
)

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")
_EMPTY = str(_DIR / "empty-section.abw")
_TWO_PARA = str(_DIR / "two-paragraphs.abw")


class TestAbwCharPerParagraph:
    def test_return_type(self):
        assert isinstance(abw_char_per_paragraph(_MINIMAL), (int, float))

    def test_exact_5_for_minimal(self):
        assert abw_char_per_paragraph(_MINIMAL) == 5.0

    def test_zero_for_empty_section(self):
        assert abw_char_per_paragraph(_EMPTY) == 0.0

    def test_exact_16_5_for_two_paragraphs(self):
        assert abw_char_per_paragraph(_TWO_PARA) == 16.5

    def test_nonnegative(self):
        assert abw_char_per_paragraph(_MINIMAL) >= 0


class TestAbwIsEmptyDocument:
    def test_return_type(self):
        assert isinstance(abw_is_empty_document(_MINIMAL), bool)

    def test_false_for_minimal(self):
        assert abw_is_empty_document(_MINIMAL) is False

    def test_true_for_empty_section(self):
        assert abw_is_empty_document(_EMPTY) is True

    def test_false_for_two_paragraphs(self):
        assert abw_is_empty_document(_TWO_PARA) is False

    def test_consistent_across_calls(self):
        assert abw_is_empty_document(_MINIMAL) == abw_is_empty_document(_MINIMAL)


class TestAbwFileSizeBytes:
    def test_return_type(self):
        assert isinstance(abw_file_size_bytes(_MINIMAL), int)

    def test_matches_os_file_size_for_minimal(self):
        from pathlib import Path
        assert abw_file_size_bytes(_MINIMAL) == Path(_MINIMAL).stat().st_size

    def test_matches_os_file_size_for_empty_section(self):
        from pathlib import Path
        assert abw_file_size_bytes(_EMPTY) == Path(_EMPTY).stat().st_size

    def test_positive(self):
        assert abw_file_size_bytes(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert abw_file_size_bytes(_MINIMAL) == abw_file_size_bytes(_MINIMAL)


class TestAbwMaxWordCountPara:
    def test_return_type(self):
        assert isinstance(abw_max_word_count_para(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        assert abw_max_word_count_para(_MINIMAL) == 1

    def test_zero_for_empty_section(self):
        assert abw_max_word_count_para(_EMPTY) == 0

    def test_exact_2_for_two_paragraphs(self):
        assert abw_max_word_count_para(_TWO_PARA) == 2

    def test_nonnegative(self):
        assert abw_max_word_count_para(_MINIMAL) >= 0


class TestAbwMinWordCountPara:
    def test_return_type(self):
        assert isinstance(abw_min_word_count_para(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        assert abw_min_word_count_para(_MINIMAL) == 1

    def test_zero_for_empty_section(self):
        assert abw_min_word_count_para(_EMPTY) == 0

    def test_min_lte_max(self):
        assert abw_min_word_count_para(_TWO_PARA) <= abw_max_word_count_para(_TWO_PARA)

    def test_nonnegative(self):
        assert abw_min_word_count_para(_MINIMAL) >= 0


class TestAbwDigitCharCount:
    def test_return_type(self):
        assert isinstance(abw_digit_char_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert abw_digit_char_count(_MINIMAL) == 0

    def test_zero_for_empty_section(self):
        assert abw_digit_char_count(_EMPTY) == 0

    def test_nonnegative(self):
        assert abw_digit_char_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_digit_char_count(_MINIMAL) == abw_digit_char_count(_MINIMAL)
