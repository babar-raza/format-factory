"""Tests for FODT Sprint 61 gap closure.

Closes:
  GAP-FODT-FOSS-FODT_CONSONA-001   (Fodt Consonant Ratio)
  GAP-FODT-FOSS-FODT_AVG_RUN-001   (Fodt Avg Run Count)
  GAP-FODT-FOSS-FODT_EMPTY_B-001   (Fodt Empty Block Count)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_consonant_ratio, fodt_avg_run_count, fodt_empty_block_count

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")
_LIST = str(_DIR / "list-basic.fodt")
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")
_TABLE = str(_DIR / "table-basic.fodt")


class TestFodtConsonantRatio:
    def test_return_type(self):
        assert isinstance(fodt_consonant_ratio(_MINIMAL), (int, float))

    def test_exact_0_7_for_minimal(self):
        assert fodt_consonant_ratio(_MINIMAL) == pytest.approx(0.7, rel=1e-3)

    def test_approx_for_headings(self):
        assert fodt_consonant_ratio(_HEADINGS) == pytest.approx(0.6207, rel=1e-2)

    def test_approx_for_list(self):
        assert fodt_consonant_ratio(_LIST) == pytest.approx(0.6389, rel=1e-2)

    def test_between_0_and_1(self):
        assert 0.0 <= fodt_consonant_ratio(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert fodt_consonant_ratio(_MINIMAL) == fodt_consonant_ratio(_MINIMAL)


class TestFodtAvgRunCount:
    def test_return_type(self):
        assert isinstance(fodt_avg_run_count(_MINIMAL), (int, float))

    def test_exact_1_0_for_minimal(self):
        assert fodt_avg_run_count(_MINIMAL) == 1.0

    def test_exact_1_0_for_list(self):
        assert fodt_avg_run_count(_LIST) == 1.0

    def test_exact_1_0_for_headings(self):
        assert fodt_avg_run_count(_HEADINGS) == 1.0

    def test_exact_1_0_for_table(self):
        assert fodt_avg_run_count(_TABLE) == 1.0

    def test_positive(self):
        assert fodt_avg_run_count(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fodt_avg_run_count(_MINIMAL) == fodt_avg_run_count(_MINIMAL)


class TestFodtEmptyBlockCount:
    def test_return_type(self):
        assert isinstance(fodt_empty_block_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert fodt_empty_block_count(_MINIMAL) == 0

    def test_zero_for_list(self):
        assert fodt_empty_block_count(_LIST) == 0

    def test_zero_for_headings(self):
        assert fodt_empty_block_count(_HEADINGS) == 0

    def test_nonnegative(self):
        assert fodt_empty_block_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodt_empty_block_count(_MINIMAL) == fodt_empty_block_count(_MINIMAL)
