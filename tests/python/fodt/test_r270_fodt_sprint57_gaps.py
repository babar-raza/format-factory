"""Tests for FODT Sprint 57 gap closure (batch 2).

Closes:
  GAP-FODT-FOSS-FODT_DIGIT_C-001   (Fodt Digit Count)
  GAP-FODT-FOSS-FODT_MAX_RUN-001   (Fodt Max Run Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_digit_count, fodt_max_run_count

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_LIST = str(_DIR / "list-basic.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_TABLE = str(_DIR / "table-basic.fodt")


class TestFodtDigitCount:
    def test_return_type(self):
        assert isinstance(fodt_digit_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert fodt_digit_count(_MINIMAL) == 0

    def test_zero_for_list(self):
        assert fodt_digit_count(_LIST) == 0

    def test_zero_for_headings(self):
        assert fodt_digit_count(_HEADINGS) == 0

    def test_zero_for_table(self):
        assert fodt_digit_count(_TABLE) == 0

    def test_nonnegative(self):
        assert fodt_digit_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_digit_count(_MINIMAL) == fodt_digit_count(_MINIMAL)


class TestFodtMaxRunCount:
    def test_return_type(self):
        assert isinstance(fodt_max_run_count(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        assert fodt_max_run_count(_MINIMAL) == 1

    def test_exact_1_for_list(self):
        assert fodt_max_run_count(_LIST) == 1

    def test_exact_1_for_headings(self):
        assert fodt_max_run_count(_HEADINGS) == 1

    def test_exact_1_for_table(self):
        assert fodt_max_run_count(_TABLE) == 1

    def test_positive(self):
        assert fodt_max_run_count(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fodt_max_run_count(_MINIMAL) == fodt_max_run_count(_MINIMAL)
