"""Tests for FODT Sprint 46 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_UPPERCA-001  (Fodt Uppercase Char Count)
  GAP-FODT-FOSS-FODT_LOWERCA-001  (Fodt Lowercase Char Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_uppercase_char_count, fodt_lowercase_char_count

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_LIST = str(_DIR / "list-basic.fodt")


class TestFodtUppercaseCharCount:
    def test_return_type(self):
        assert isinstance(fodt_uppercase_char_count(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        assert fodt_uppercase_char_count(_MINIMAL) == 1

    def test_exact_19_for_headings(self):
        assert fodt_uppercase_char_count(_HEADINGS) == 19

    def test_exact_2_for_list(self):
        assert fodt_uppercase_char_count(_LIST) == 2

    def test_nonnegative(self):
        assert fodt_uppercase_char_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_uppercase_char_count(_MINIMAL) == fodt_uppercase_char_count(_MINIMAL)


class TestFodtLowercaseCharCount:
    def test_return_type(self):
        assert isinstance(fodt_lowercase_char_count(_MINIMAL), int)

    def test_exact_9_for_minimal(self):
        assert fodt_lowercase_char_count(_MINIMAL) == 9

    def test_exact_213_for_headings(self):
        assert fodt_lowercase_char_count(_HEADINGS) == 213

    def test_exact_34_for_list(self):
        assert fodt_lowercase_char_count(_LIST) == 34

    def test_nonnegative(self):
        assert fodt_lowercase_char_count(_MINIMAL) >= 0

    def test_lower_gte_upper_for_typical_docs(self):
        # Most text is lowercase
        assert fodt_lowercase_char_count(_HEADINGS) > fodt_uppercase_char_count(_HEADINGS)
