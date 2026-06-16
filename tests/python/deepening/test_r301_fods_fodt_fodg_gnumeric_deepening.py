"""Sprint 71 — FODS / FODT / FODG / Gnumeric product deepening (R301).

Tests 8 new analytics functions:
  FODS: fods_has_string_cells, fods_row_count_variance
  FODT: fodt_whitespace_ratio, fodt_longest_word
  FODG: fodg_avg_text_per_shape, fodg_min_text_per_page
  Gnumeric: gnumeric_is_all_numeric, gnumeric_nonempty_cell_ratio
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods, fods_has_string_cells, fods_row_count_variance
from src.python.fodt import fodt_whitespace_ratio, fodt_longest_word
from src.python.fodg import fodg_avg_text_per_shape, fodg_min_text_per_page
from src.python.gnumeric import gnumeric_is_all_numeric, gnumeric_nonempty_cell_ratio

_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_FODT = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
_FODG = _REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"


class TestFodsHasStringCells:
    def test_returns_bool(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_has_string_cells(wb), bool)


class TestFodsRowCountVariance:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_row_count_variance(wb), (int, float))

    def test_nonnegative(self):
        wb = parse_fods(_FODS)
        assert fods_row_count_variance(wb) >= 0.0


class TestFodtWhitespaceRatio:
    def test_returns_float(self):
        assert isinstance(fodt_whitespace_ratio(_FODT), (int, float))

    def test_between_zero_and_one(self):
        ratio = fodt_whitespace_ratio(_FODT)
        assert 0.0 <= ratio <= 1.0


class TestFodtLongestWord:
    def test_returns_str(self):
        assert isinstance(fodt_longest_word(_FODT), str)


class TestFodgAvgTextPerShape:
    def test_returns_float(self):
        assert isinstance(fodg_avg_text_per_shape(_FODG), (int, float))

    def test_nonnegative(self):
        assert fodg_avg_text_per_shape(_FODG) >= 0.0


class TestFodgMinTextPerPage:
    def test_returns_int(self):
        assert isinstance(fodg_min_text_per_page(_FODG), int)

    def test_nonnegative(self):
        assert fodg_min_text_per_page(_FODG) >= 0


class TestGnumericIsAllNumeric:
    def test_returns_bool(self):
        assert isinstance(gnumeric_is_all_numeric(_GNUMERIC), bool)


class TestGnumericNonemptyCellRatio:
    def test_returns_float(self):
        assert isinstance(gnumeric_nonempty_cell_ratio(_GNUMERIC), (int, float))

    def test_between_zero_and_one(self):
        ratio = gnumeric_nonempty_cell_ratio(_GNUMERIC)
        assert 0.0 <= ratio <= 1.0
