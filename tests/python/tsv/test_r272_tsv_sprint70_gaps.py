"""Tests for TSV Sprint 70 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_HEADER_F-001   (Tsv Header Field Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_header_field_count

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")


class TestTsvHeaderFieldCount:
    def test_return_type(self):
        assert isinstance(tsv_header_field_count(_MINIMAL), int)

    def test_exact_2_for_minimal(self):
        assert tsv_header_field_count(_MINIMAL) == 2

    def test_exact_4_for_multi(self):
        assert tsv_header_field_count(_MULTI) == 4

    def test_exact_1_for_single(self):
        assert tsv_header_field_count(_SINGLE) == 1

    def test_positive(self):
        assert tsv_header_field_count(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert tsv_header_field_count(_MINIMAL) == tsv_header_field_count(_MINIMAL)
