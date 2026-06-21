"""
FODT FOSS gap closure tests.

Closes:
  GAP-FODT-FOSS-FODT_LONGEST-001  — fodt_longest_word
  GAP-FODT-FOSS-FODT_AVG_HEA-001  — fodt_avg_heading_length
  GAP-FODT-FOSS-FODT_TABLE_D-001  — fodt_table_density
  GAP-FODT-FOSS-FODT_TOTAL_T-001  — fodt_total_table_cells
  GAP-FODT-FOSS-FODT_HAS_NUM-001  — fodt_has_numeric_content
  GAP-FODT-FOSS-FODT_AVG_SEN-001  — fodt_avg_sentence_length
  GAP-FODT-FOSS-FODT_MAX_HEA-001  — fodt_max_heading_depth
  GAP-FODT-FOSS-FODT_TOTAL_C-001  — fodt_total_char_count
  GAP-FODT-FOSS-FODT_IS_TEXT-001  — fodt_is_text_heavy

Run from repo root:
    python -m pytest tests/python/fodt/test_fodt_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

import fodt

SAMPLES = REPO_ROOT / "samples" / "by-format" / "fodt"
MINIMAL = SAMPLES / "minimal-document.fodt"
HEADINGS = SAMPLES / "headings-and-paragraphs.fodt"
TABLE = SAMPLES / "table-basic.fodt"


class TestFodtLongestWord:
    def test_minimal_returns_word(self):
        assert fodt.fodt_longest_word(MINIMAL) == 'Hello'

    def test_headings_longer_word(self):
        result = fodt.fodt_longest_word(HEADINGS)
        assert len(result) > len(fodt.fodt_longest_word(MINIMAL))

    def test_returns_str(self):
        assert isinstance(fodt.fodt_longest_word(MINIMAL), str)


class TestFodtAvgHeadingLength:
    def test_minimal_no_headings(self):
        assert fodt.fodt_avg_heading_length(MINIMAL) == pytest.approx(0.0, abs=0.01)

    def test_headings_positive(self):
        assert fodt.fodt_avg_heading_length(HEADINGS) > 0

    def test_returns_numeric(self):
        assert isinstance(fodt.fodt_avg_heading_length(MINIMAL), (int, float))

    def test_non_negative(self):
        for p in [MINIMAL, HEADINGS, TABLE]:
            assert fodt.fodt_avg_heading_length(p) >= 0


class TestFodtTableDensity:
    def test_minimal_zero(self):
        assert fodt.fodt_table_density(MINIMAL) == pytest.approx(0.0, abs=0.01)

    def test_table_positive(self):
        assert fodt.fodt_table_density(TABLE) > 0

    def test_returns_numeric(self):
        assert isinstance(fodt.fodt_table_density(MINIMAL), (int, float))

    def test_non_negative(self):
        for p in [MINIMAL, HEADINGS, TABLE]:
            assert fodt.fodt_table_density(p) >= 0


class TestFodtTotalTableCells:
    def test_returns_int(self):
        assert isinstance(fodt.fodt_total_table_cells(MINIMAL), int)

    def test_non_negative(self):
        for p in [MINIMAL, HEADINGS, TABLE]:
            assert fodt.fodt_total_table_cells(p) >= 0


class TestFodtHasNumericContent:
    def test_returns_bool(self):
        assert isinstance(fodt.fodt_has_numeric_content(MINIMAL), bool)

    def test_minimal_no_numeric(self):
        assert fodt.fodt_has_numeric_content(MINIMAL) is False


class TestFodtAvgSentenceLength:
    def test_returns_numeric(self):
        assert isinstance(fodt.fodt_avg_sentence_length(MINIMAL), (int, float))

    def test_non_negative(self):
        for p in [MINIMAL, HEADINGS, TABLE]:
            assert fodt.fodt_avg_sentence_length(p) >= 0


class TestFodtMaxHeadingDepth:
    def test_minimal_zero(self):
        assert fodt.fodt_max_heading_depth(MINIMAL) == 0

    def test_headings_positive(self):
        assert fodt.fodt_max_heading_depth(HEADINGS) > 0

    def test_returns_int(self):
        assert isinstance(fodt.fodt_max_heading_depth(MINIMAL), int)

    def test_non_negative(self):
        for p in [MINIMAL, HEADINGS, TABLE]:
            assert fodt.fodt_max_heading_depth(p) >= 0


class TestFodtTotalCharCount:
    def test_minimal_positive(self):
        assert fodt.fodt_total_char_count(MINIMAL) > 0

    def test_headings_more_than_minimal(self):
        assert fodt.fodt_total_char_count(HEADINGS) > fodt.fodt_total_char_count(MINIMAL)

    def test_returns_int(self):
        assert isinstance(fodt.fodt_total_char_count(MINIMAL), int)


class TestFodtIsTextHeavy:
    def test_minimal_not_heavy(self):
        assert fodt.fodt_is_text_heavy(MINIMAL) is False

    def test_headings_is_heavy(self):
        assert fodt.fodt_is_text_heavy(HEADINGS) is True

    def test_returns_bool(self):
        assert isinstance(fodt.fodt_is_text_heavy(MINIMAL), bool)
