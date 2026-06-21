"""Tests for FODT gap closure (Sprint 40).

Closes:
  GAP-FODT-FOSS-FODT_WHITESP-001  (Fodt Whitespace Ratio)
  GAP-FODT-FOSS-FODT_LONGEST-001  (Fodt Longest Word)
  GAP-FODT-FOSS-FODT_AVG_HEA-001  (Fodt Avg Heading Length)
  GAP-FODT-FOSS-FODT_TABLE_D-001  (Fodt Table Density)
  GAP-FODT-FOSS-FODT_TOTAL_T-001  (Fodt Total Table Cells)
  GAP-FODT-FOSS-FODT_HAS_NUM-001  (Fodt Has Numeric Content)
  GAP-FODT-FOSS-FODT_AVG_SEN-001  (Fodt Avg Sentence Length)
  GAP-FODT-FOSS-FODT_MAX_HEA-001  (Fodt Max Heading Depth)
  GAP-FODT-FOSS-FODT_TOTAL_C-001  (Fodt Total Char Count)
  GAP-FODT-FOSS-FODT_IS_TEXT-001  (Fodt Is Text Heavy)
"""
import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import (
    fodt_avg_heading_length,
    fodt_avg_sentence_length,
    fodt_has_numeric_content,
    fodt_is_text_heavy,
    fodt_longest_word,
    fodt_max_heading_depth,
    fodt_table_density,
    fodt_total_char_count,
    fodt_total_table_cells,
    fodt_whitespace_ratio,
)

_DIR = _REPO / "samples" / "by-format" / "fodt"
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_MINIMAL = str(_DIR / "minimal-document.fodt")
_TABLE = str(_DIR / "table-basic.fodt")
_LIST = str(_DIR / "list-basic.fodt")


class TestFodtWhitespaceRatio:
    def test_return_type(self):
        assert isinstance(fodt_whitespace_ratio(_MINIMAL), float)

    def test_nonzero_for_minimal(self):
        # "Hello world" has spaces -> nonzero whitespace ratio
        ratio = fodt_whitespace_ratio(_MINIMAL)
        assert math.isclose(ratio, 0.07692307692307693, rel_tol=1e-6)

    def test_between_0_and_1(self):
        ratio = fodt_whitespace_ratio(_MINIMAL)
        assert 0.0 <= ratio <= 1.0

    def test_positive_for_headings(self):
        assert fodt_whitespace_ratio(_HEADINGS) > 0

    def test_consistent_across_calls(self):
        assert fodt_whitespace_ratio(_MINIMAL) == fodt_whitespace_ratio(_MINIMAL)


class TestFodtLongestWord:
    def test_return_type(self):
        assert isinstance(fodt_longest_word(_MINIMAL), str)

    def test_exact_hello_for_minimal(self):
        assert fodt_longest_word(_MINIMAL) == "Hello"

    def test_demonstrates_for_headings(self):
        assert fodt_longest_word(_HEADINGS) == "demonstrates"

    def test_nonempty(self):
        assert len(fodt_longest_word(_MINIMAL)) >= 1

    def test_consistent_across_calls(self):
        assert fodt_longest_word(_MINIMAL) == fodt_longest_word(_MINIMAL)


class TestFodtAvgHeadingLength:
    def test_return_type(self):
        assert isinstance(fodt_avg_heading_length(_MINIMAL), float)

    def test_zero_for_minimal_no_headings(self):
        assert fodt_avg_heading_length(_MINIMAL) == 0.0

    def test_nonzero_for_headings(self):
        # headings-and-paragraphs has headings
        assert fodt_avg_heading_length(_HEADINGS) > 0

    def test_nonnegative(self):
        assert fodt_avg_heading_length(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert fodt_avg_heading_length(_HEADINGS) == fodt_avg_heading_length(_HEADINGS)


class TestFodtTableDensity:
    def test_return_type(self):
        assert isinstance(fodt_table_density(_MINIMAL), float)

    def test_zero_for_minimal_no_tables(self):
        assert fodt_table_density(_MINIMAL) == 0.0

    def test_zero_for_list(self):
        assert fodt_table_density(_LIST) == 0.0

    def test_nonnegative(self):
        assert fodt_table_density(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert fodt_table_density(_MINIMAL) == fodt_table_density(_MINIMAL)


class TestFodtTotalTableCells:
    def test_return_type(self):
        assert isinstance(fodt_total_table_cells(_MINIMAL), int)

    def test_zero_for_minimal_no_tables(self):
        assert fodt_total_table_cells(_MINIMAL) == 0

    def test_zero_for_headings_no_tables(self):
        assert fodt_total_table_cells(_HEADINGS) == 0

    def test_nonnegative(self):
        assert fodt_total_table_cells(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_total_table_cells(_MINIMAL) == fodt_total_table_cells(_MINIMAL)


class TestFodtHasNumericContent:
    def test_return_type(self):
        assert isinstance(fodt_has_numeric_content(_MINIMAL), bool)

    def test_false_for_minimal(self):
        assert fodt_has_numeric_content(_MINIMAL) is False

    def test_false_for_headings(self):
        assert fodt_has_numeric_content(_HEADINGS) is False

    def test_consistent_across_calls(self):
        assert fodt_has_numeric_content(_MINIMAL) == fodt_has_numeric_content(_MINIMAL)


class TestFodtAvgSentenceLength:
    def test_return_type(self):
        assert isinstance(fodt_avg_sentence_length(_MINIMAL), float)

    def test_exact_12_0_for_minimal(self):
        assert fodt_avg_sentence_length(_MINIMAL) == 12.0

    def test_exact_45_0_for_headings(self):
        assert fodt_avg_sentence_length(_HEADINGS) == 45.0

    def test_positive(self):
        assert fodt_avg_sentence_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fodt_avg_sentence_length(_MINIMAL) == fodt_avg_sentence_length(_MINIMAL)


class TestFodtMaxHeadingDepth:
    def test_return_type(self):
        assert isinstance(fodt_max_heading_depth(_MINIMAL), int)

    def test_zero_for_minimal_no_headings(self):
        assert fodt_max_heading_depth(_MINIMAL) == 0

    def test_exact_1_for_headings(self):
        assert fodt_max_heading_depth(_HEADINGS) == 1

    def test_nonnegative(self):
        assert fodt_max_heading_depth(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_max_heading_depth(_HEADINGS) == fodt_max_heading_depth(_HEADINGS)


class TestFodtTotalCharCount:
    def test_return_type(self):
        assert isinstance(fodt_total_char_count(_MINIMAL), int)

    def test_exact_13_for_minimal(self):
        assert fodt_total_char_count(_MINIMAL) == 13

    def test_exact_237_for_headings(self):
        assert fodt_total_char_count(_HEADINGS) == 237

    def test_positive(self):
        assert fodt_total_char_count(_MINIMAL) >= 1

    def test_consistent_across_calls(self):
        assert fodt_total_char_count(_MINIMAL) == fodt_total_char_count(_MINIMAL)


class TestFodtIsTextHeavy:
    def test_return_type(self):
        assert isinstance(fodt_is_text_heavy(_MINIMAL), bool)

    def test_false_for_minimal_short(self):
        assert fodt_is_text_heavy(_MINIMAL) is False

    def test_true_for_headings_long(self):
        assert fodt_is_text_heavy(_HEADINGS) is True

    def test_consistent_across_calls(self):
        assert fodt_is_text_heavy(_MINIMAL) == fodt_is_text_heavy(_MINIMAL)
