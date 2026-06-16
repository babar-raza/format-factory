"""Sprint 58 — PGM / PBM / TSV / FODP product deepening (R288).

Tests 8 new analytics functions:
  PGM:  pgm_megapixels, pgm_is_tall
  PBM:  pbm_dimension_ratio, pbm_megapixels
  TSV:  tsv_row_length_variance, tsv_column_type_counts
  FODP: fodp_text_length_variance, fodp_slide_text_lengths
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_megapixels, pgm_is_tall
from src.python.pbm import pbm_dimension_ratio, pbm_megapixels
from src.python.tsv import tsv_row_length_variance, tsv_column_type_counts
from src.python.fodp import fodp_text_length_variance, fodp_slide_text_lengths

_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"
_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
_FODP = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"


class TestPgmMegapixels:
    def test_returns_float(self):
        assert isinstance(pgm_megapixels(_PGM), (int, float))

    def test_small(self):
        assert pgm_megapixels(_PGM) < 1.0


class TestPgmIsTall:
    def test_returns_bool(self):
        assert isinstance(pgm_is_tall(_PGM), bool)

    def test_square_not_tall(self):
        assert pgm_is_tall(_PGM) is False


class TestPbmDimensionRatio:
    def test_returns_float(self):
        assert isinstance(pbm_dimension_ratio(_PBM), (int, float))

    def test_positive(self):
        assert pbm_dimension_ratio(_PBM) > 0.0


class TestPbmMegapixels:
    def test_returns_float(self):
        assert isinstance(pbm_megapixels(_PBM), (int, float))

    def test_small(self):
        assert pbm_megapixels(_PBM) < 1.0


class TestTsvRowLengthVariance:
    def test_returns_float(self):
        assert isinstance(tsv_row_length_variance(_TSV), (int, float))

    def test_nonnegative(self):
        assert tsv_row_length_variance(_TSV) >= 0.0


class TestTsvColumnTypeCounts:
    def test_returns_dict(self):
        result = tsv_column_type_counts(_TSV)
        assert isinstance(result, dict)
        assert "numeric" in result
        assert "string" in result


class TestFodpTextLengthVariance:
    def test_returns_float(self):
        assert isinstance(fodp_text_length_variance(_FODP), (int, float))

    def test_nonnegative(self):
        assert fodp_text_length_variance(_FODP) >= 0.0


class TestFodpSlideTextLengths:
    def test_returns_list(self):
        result = fodp_slide_text_lengths(_FODP)
        assert isinstance(result, list)

    def test_returns_ints(self):
        result = fodp_slide_text_lengths(_FODP)
        for v in result:
            assert isinstance(v, int)
