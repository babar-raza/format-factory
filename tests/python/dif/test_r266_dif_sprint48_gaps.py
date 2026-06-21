"""Tests for DIF Sprint 48 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_UNIQUE_R-001  (Dif Unique Row Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_unique_row_count

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")
_NUMERIC = str(_DIR / "numeric-row.dif")
_SINGLE = str(_DIR / "single-cell.dif")


class TestDifUniqueRowCount:
    def test_return_type(self):
        assert isinstance(dif_unique_row_count(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        assert dif_unique_row_count(_MINIMAL) == 1

    def test_exact_1_for_numeric_row(self):
        assert dif_unique_row_count(_NUMERIC) == 1

    def test_exact_1_for_single_cell(self):
        assert dif_unique_row_count(_SINGLE) == 1

    def test_positive(self):
        assert dif_unique_row_count(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert dif_unique_row_count(_MINIMAL) == dif_unique_row_count(_MINIMAL)
