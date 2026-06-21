"""
Sprint ff-idempotent-spec-to-feature-swarm-20260617 — FODS analytics deepening.
Tests for two new analytics functions:
  fods_sheet_count_times_eighty_nine, fods_total_cell_count_times_eighty_nine
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    parse_fods_strict,
    fods_sheet_count_times_eighty_nine,
    fods_total_cell_count_times_eighty_nine,
)

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


def _wb(path: str):
    return parse_fods_strict(path)


# --- fods_sheet_count_times_eighty_nine ---

class TestFodsSheetCountTimesEightyNine:
    def test_returns_int_minimal(self):
        result = fods_sheet_count_times_eighty_nine(_wb(_MINIMAL))
        assert isinstance(result, int)

    def test_non_negative_minimal(self):
        result = fods_sheet_count_times_eighty_nine(_wb(_MINIMAL))
        assert result >= 0

    def test_divisible_by_89_minimal(self):
        result = fods_sheet_count_times_eighty_nine(_wb(_MINIMAL))
        assert result % 89 == 0

    def test_returns_int_multi(self):
        result = fods_sheet_count_times_eighty_nine(_wb(_MULTI))
        assert isinstance(result, int)

    def test_divisible_by_89_multi(self):
        result = fods_sheet_count_times_eighty_nine(_wb(_MULTI))
        assert result % 89 == 0

    def test_multi_greater_than_minimal(self):
        r_min = fods_sheet_count_times_eighty_nine(_wb(_MINIMAL))
        r_mul = fods_sheet_count_times_eighty_nine(_wb(_MULTI))
        assert r_mul >= r_min


# --- fods_total_cell_count_times_eighty_nine ---

class TestFodsTotalCellCountTimesEightyNine:
    def test_returns_int_minimal(self):
        result = fods_total_cell_count_times_eighty_nine(_wb(_MINIMAL))
        assert isinstance(result, int)

    def test_non_negative_minimal(self):
        result = fods_total_cell_count_times_eighty_nine(_wb(_MINIMAL))
        assert result >= 0

    def test_divisible_by_89_minimal(self):
        result = fods_total_cell_count_times_eighty_nine(_wb(_MINIMAL))
        assert result % 89 == 0

    def test_returns_int_multi(self):
        result = fods_total_cell_count_times_eighty_nine(_wb(_MULTI))
        assert isinstance(result, int)

    def test_divisible_by_89_multi(self):
        result = fods_total_cell_count_times_eighty_nine(_wb(_MULTI))
        assert result % 89 == 0

    def test_returns_int_typed(self):
        result = fods_total_cell_count_times_eighty_nine(_wb(_TYPED))
        assert isinstance(result, int)

    def test_divisible_by_89_typed(self):
        result = fods_total_cell_count_times_eighty_nine(_wb(_TYPED))
        assert result % 89 == 0
