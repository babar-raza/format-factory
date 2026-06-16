"""Sprint 68 — FODS / FODT / FODG / Gnumeric product deepening (R298).

Tests 8 new analytics functions:
  FODS: fods_total_row_count, fods_avg_col_count
  FODT: fodt_unique_word_count, fodt_is_multi_paragraph
  FODG: fodg_page_text_variance, fodg_total_text_chars
  Gnumeric: gnumeric_has_empty_cells, gnumeric_total_row_count
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods, fods_total_row_count, fods_avg_col_count
from src.python.fodt import fodt_unique_word_count, fodt_is_multi_paragraph
from src.python.fodg import fodg_page_text_variance, fodg_total_text_chars
from src.python.gnumeric import gnumeric_has_empty_cells, gnumeric_total_row_count

_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_FODT = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
_FODG = _REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"


class TestFodsTotalRowCount:
    def test_returns_int(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_total_row_count(wb), int)

    def test_nonnegative(self):
        wb = parse_fods(_FODS)
        assert fods_total_row_count(wb) >= 0


class TestFodsAvgColCount:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_avg_col_count(wb), (int, float))


class TestFodtUniqueWordCount:
    def test_returns_int(self):
        assert isinstance(fodt_unique_word_count(_FODT), int)

    def test_nonnegative(self):
        assert fodt_unique_word_count(_FODT) >= 0


class TestFodtIsMultiParagraph:
    def test_returns_bool(self):
        assert isinstance(fodt_is_multi_paragraph(_FODT), bool)


class TestFodgPageTextVariance:
    def test_returns_float(self):
        assert isinstance(fodg_page_text_variance(_FODG), (int, float))

    def test_nonnegative(self):
        assert fodg_page_text_variance(_FODG) >= 0.0


class TestFodgTotalTextChars:
    def test_returns_int(self):
        assert isinstance(fodg_total_text_chars(_FODG), int)

    def test_nonnegative(self):
        assert fodg_total_text_chars(_FODG) >= 0


class TestGnumericHasEmptyCells:
    def test_returns_bool(self):
        assert isinstance(gnumeric_has_empty_cells(_GNUMERIC), bool)


class TestGnumericTotalRowCount:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count(_GNUMERIC), int)

    def test_nonnegative(self):
        assert gnumeric_total_row_count(_GNUMERIC) >= 0
