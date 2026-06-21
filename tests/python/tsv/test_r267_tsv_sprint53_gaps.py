"""Tests for TSV Sprint 53 gap closure.

Closes:
  GAP-TSV-FOSS-TSV_MAX_FIEL-001  (Tsv Max Field Value Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_max_field_value_length

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")
_MULTI = str(_DIR / "multi-column.tsv")
_SINGLE = str(_DIR / "single-cell.tsv")


class TestTsvMaxFieldValueLength:
    def test_return_type(self):
        assert isinstance(tsv_max_field_value_length(_MINIMAL), int)

    def test_exact_5_for_minimal(self):
        assert tsv_max_field_value_length(_MINIMAL) == 5

    def test_exact_5_for_multi_column(self):
        assert tsv_max_field_value_length(_MULTI) == 5

    def test_exact_5_for_single_cell(self):
        assert tsv_max_field_value_length(_SINGLE) == 5

    def test_positive(self):
        assert tsv_max_field_value_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert tsv_max_field_value_length(_MINIMAL) == tsv_max_field_value_length(_MINIMAL)
