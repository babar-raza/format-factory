"""
test_r321_odt_new_analytics.py
Sprint 57 — 5 new ODT analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    odt_file_size_bytes,
    odt_max_word_count_para,
    odt_min_word_count_para,
    odt_unique_paragraph_count,
    odt_avg_char_count_per_para,
)

_VALID = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = str(_VALID / "minimal-document.odt")
_TWO = str(_VALID / "two-paragraphs.odt")
_UNICODE = str(_VALID / "unicode-text.odt")


# --- odt_file_size_bytes ---

class TestOdtFileSizeBytes:
    def test_minimal_positive(self):
        assert odt_file_size_bytes(_MINIMAL) > 0

    def test_two_positive(self):
        assert odt_file_size_bytes(_TWO) > 0

    def test_unicode_positive(self):
        assert odt_file_size_bytes(_UNICODE) > 0

    def test_returns_int(self):
        assert isinstance(odt_file_size_bytes(_MINIMAL), int)

    def test_reasonable_size(self):
        assert odt_file_size_bytes(_MINIMAL) >= 100


# --- odt_max_word_count_para ---

class TestOdtMaxWordCountPara:
    def test_returns_int(self):
        assert isinstance(odt_max_word_count_para(_TWO), int)

    def test_two_positive(self):
        assert odt_max_word_count_para(_TWO) >= 1

    def test_minimal_non_negative(self):
        assert odt_max_word_count_para(_MINIMAL) >= 0

    def test_unicode_non_negative(self):
        assert odt_max_word_count_para(_UNICODE) >= 0

    def test_max_ge_min(self):
        assert odt_max_word_count_para(_TWO) >= odt_min_word_count_para(_TWO)


# --- odt_min_word_count_para ---

class TestOdtMinWordCountPara:
    def test_returns_int(self):
        assert isinstance(odt_min_word_count_para(_TWO), int)

    def test_two_non_negative(self):
        assert odt_min_word_count_para(_TWO) >= 0

    def test_minimal_non_negative(self):
        assert odt_min_word_count_para(_MINIMAL) >= 0

    def test_unicode_non_negative(self):
        assert odt_min_word_count_para(_UNICODE) >= 0

    def test_min_le_max(self):
        assert odt_min_word_count_para(_TWO) <= odt_max_word_count_para(_TWO)


# --- odt_unique_paragraph_count ---

class TestOdtUniqueParagraphCount:
    def test_returns_int(self):
        assert isinstance(odt_unique_paragraph_count(_TWO), int)

    def test_two_at_least_one(self):
        assert odt_unique_paragraph_count(_TWO) >= 1

    def test_minimal_non_negative(self):
        assert odt_unique_paragraph_count(_MINIMAL) >= 0

    def test_unicode_at_least_one(self):
        assert odt_unique_paragraph_count(_UNICODE) >= 1

    def test_non_negative(self):
        assert odt_unique_paragraph_count(_TWO) >= 0


# --- odt_avg_char_count_per_para ---

class TestOdtAvgCharCountPerPara:
    def test_returns_float(self):
        assert isinstance(odt_avg_char_count_per_para(_TWO), float)

    def test_two_positive(self):
        assert odt_avg_char_count_per_para(_TWO) > 0.0

    def test_minimal_non_negative(self):
        assert odt_avg_char_count_per_para(_MINIMAL) >= 0.0

    def test_unicode_non_negative(self):
        assert odt_avg_char_count_per_para(_UNICODE) >= 0.0

    def test_non_negative(self):
        assert odt_avg_char_count_per_para(_TWO) >= 0.0
