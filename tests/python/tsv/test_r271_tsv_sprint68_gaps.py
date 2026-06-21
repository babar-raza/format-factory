"""Tests for TSV Sprint 68 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_TOTAL_HE-001   (Tsv Total Header Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_total_header_length

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")


class TestTsvTotalHeaderLength:
    def test_return_type(self):
        assert isinstance(tsv_total_header_length(_MINIMAL), int)

    def test_exact_7_for_minimal(self):
        assert tsv_total_header_length(_MINIMAL) == 7

    def test_exact_15_for_multi(self):
        assert tsv_total_header_length(_MULTI) == 15

    def test_exact_5_for_single(self):
        assert tsv_total_header_length(_SINGLE) == 5

    def test_positive(self):
        assert tsv_total_header_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert tsv_total_header_length(_MINIMAL) == tsv_total_header_length(_MINIMAL)
