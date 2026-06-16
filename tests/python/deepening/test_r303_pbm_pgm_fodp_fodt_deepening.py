"""Sprint 73 — PBM / PGM / FODP / FODT product deepening (R303).

Tests 8 new analytics functions:
  PBM: pbm_avg_row_density, pbm_border_black_count
  PGM: pgm_is_high_contrast, pgm_avg_row_brightness
  FODP: fodp_min_title_length, fodp_image_density
  FODT: fodt_avg_heading_length, fodt_table_density
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_avg_row_density, pbm_border_black_count
from src.python.pgm import pgm_is_high_contrast, pgm_avg_row_brightness
from src.python.fodp import fodp_min_title_length, fodp_image_density
from src.python.fodt import fodt_avg_heading_length, fodt_table_density

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
_FODT = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"


class TestPbmAvgRowDensity:
    def test_returns_float(self):
        assert isinstance(pbm_avg_row_density(_PBM), float)

    def test_between_zero_and_one(self):
        val = pbm_avg_row_density(_PBM)
        assert 0.0 <= val <= 1.0


class TestPbmBorderBlackCount:
    def test_returns_int(self):
        assert isinstance(pbm_border_black_count(_PBM), int)

    def test_nonnegative(self):
        assert pbm_border_black_count(_PBM) >= 0


class TestPgmIsHighContrast:
    def test_returns_bool(self):
        assert isinstance(pgm_is_high_contrast(_PGM), bool)


class TestPgmAvgRowBrightness:
    def test_returns_list(self):
        result = pgm_avg_row_brightness(_PGM)
        assert isinstance(result, list)

    def test_entries_are_float(self):
        result = pgm_avg_row_brightness(_PGM)
        if result:
            assert isinstance(result[0], (int, float))


class TestFodpMinTitleLength:
    def test_returns_int(self):
        assert isinstance(fodp_min_title_length(_FODP), int)

    def test_nonnegative(self):
        assert fodp_min_title_length(_FODP) >= 0


class TestFodpImageDensity:
    def test_returns_float(self):
        assert isinstance(fodp_image_density(_FODP), (int, float))

    def test_nonnegative(self):
        assert fodp_image_density(_FODP) >= 0.0


class TestFodtAvgHeadingLength:
    def test_returns_float(self):
        assert isinstance(fodt_avg_heading_length(_FODT), (int, float))

    def test_nonnegative(self):
        assert fodt_avg_heading_length(_FODT) >= 0.0


class TestFodtTableDensity:
    def test_returns_float(self):
        assert isinstance(fodt_table_density(_FODT), (int, float))

    def test_nonnegative(self):
        assert fodt_table_density(_FODT) >= 0.0
