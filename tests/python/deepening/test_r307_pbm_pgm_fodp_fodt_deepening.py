"""Sprint 77 — PBM / PGM / FODP / FODT product deepening cycle 2 (R307).

Tests 8 new analytics functions:
  PBM: pbm_row_density_variance, pbm_is_checkerboard
  PGM: pgm_dark_pixel_ratio, pgm_row_brightness_variance
  FODP: fodp_total_text_chars, fodp_avg_title_words
  FODT: fodt_heading_to_paragraph_ratio, fodt_total_table_cells
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_row_density_variance, pbm_is_checkerboard
from src.python.pgm import pgm_dark_pixel_ratio, pgm_row_brightness_variance
from src.python.fodp import fodp_total_text_chars, fodp_avg_title_words
from src.python.fodt import fodt_heading_to_paragraph_ratio, fodt_total_table_cells

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
_FODT = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"


class TestPbmRowDensityVariance:
    def test_returns_float(self):
        assert isinstance(pbm_row_density_variance(_PBM), float)

    def test_nonnegative(self):
        assert pbm_row_density_variance(_PBM) >= 0.0


class TestPbmIsCheckerboard:
    def test_returns_bool(self):
        assert isinstance(pbm_is_checkerboard(_PBM), bool)


class TestPgmDarkPixelRatio:
    def test_returns_float(self):
        assert isinstance(pgm_dark_pixel_ratio(_PGM), float)

    def test_between_zero_and_one(self):
        val = pgm_dark_pixel_ratio(_PGM)
        assert 0.0 <= val <= 1.0


class TestPgmRowBrightnessVariance:
    def test_returns_float(self):
        assert isinstance(pgm_row_brightness_variance(_PGM), float)

    def test_nonnegative(self):
        assert pgm_row_brightness_variance(_PGM) >= 0.0


class TestFodpTotalTextChars:
    def test_returns_int(self):
        assert isinstance(fodp_total_text_chars(_FODP), int)

    def test_nonnegative(self):
        assert fodp_total_text_chars(_FODP) >= 0


class TestFodpAvgTitleWords:
    def test_returns_float(self):
        assert isinstance(fodp_avg_title_words(_FODP), (int, float))

    def test_nonnegative(self):
        assert fodp_avg_title_words(_FODP) >= 0.0


class TestFodtHeadingToParagraphRatio:
    def test_returns_float(self):
        assert isinstance(fodt_heading_to_paragraph_ratio(_FODT), float)

    def test_nonnegative(self):
        assert fodt_heading_to_paragraph_ratio(_FODT) >= 0.0


class TestFodtTotalTableCells:
    def test_returns_int(self):
        assert isinstance(fodt_total_table_cells(_FODT), int)

    def test_nonnegative(self):
        assert fodt_total_table_cells(_FODT) >= 0
