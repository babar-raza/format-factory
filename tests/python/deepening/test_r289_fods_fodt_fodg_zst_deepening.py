"""Sprint 59 — FODS / FODT / FODG / ZST product deepening (R289).

Tests 8 new analytics functions:
  FODS: fods_max_col_count, fods_empty_sheet_count
  FODT: fodt_sentence_count, fodt_words_per_sentence
  FODG: fodg_text_density, fodg_is_multi_page
  ZST:  zst_frame_median_size, zst_is_large_file
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_max_col_count, fods_empty_sheet_count
from src.python.fods.parser import parse_fods
from src.python.fodt import fodt_sentence_count, fodt_words_per_sentence
from src.python.fodg import fodg_text_density, fodg_is_multi_page
from src.python.zst import zst_frame_median_size, zst_is_large_file

_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_FODT = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"
_FODG = _REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg"
_ZST = _REPO / "samples" / "by-format" / "zst" / "valid" / "block-128k.zst"


class TestFodsMaxColCount:
    def test_returns_int(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_max_col_count(wb), int)

    def test_nonnegative(self):
        wb = parse_fods(_FODS)
        assert fods_max_col_count(wb) >= 0


class TestFodsEmptySheetCount:
    def test_returns_int(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_empty_sheet_count(wb), int)

    def test_nonnegative(self):
        wb = parse_fods(_FODS)
        assert fods_empty_sheet_count(wb) >= 0


class TestFodtSentenceCount:
    def test_returns_int(self):
        assert isinstance(fodt_sentence_count(_FODT), int)

    def test_nonnegative(self):
        assert fodt_sentence_count(_FODT) >= 0


class TestFodtWordsPerSentence:
    def test_returns_float(self):
        assert isinstance(fodt_words_per_sentence(_FODT), (int, float))

    def test_nonnegative(self):
        assert fodt_words_per_sentence(_FODT) >= 0.0


class TestFodgTextDensity:
    def test_returns_float(self):
        assert isinstance(fodg_text_density(_FODG), (int, float))

    def test_nonnegative(self):
        assert fodg_text_density(_FODG) >= 0.0


class TestFodgIsMultiPage:
    def test_returns_bool(self):
        assert isinstance(fodg_is_multi_page(_FODG), bool)


class TestZstFrameMedianSize:
    def test_returns_int(self):
        assert isinstance(zst_frame_median_size(_ZST), int)

    def test_nonnegative(self):
        assert zst_frame_median_size(_ZST) >= 0


class TestZstIsLargeFile:
    def test_returns_bool(self):
        assert isinstance(zst_is_large_file(_ZST), bool)

    def test_small_sample(self):
        assert zst_is_large_file(_ZST) is False
