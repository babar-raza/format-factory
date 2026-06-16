"""Sprint 81 — PBM/PGM/FODP/FODT product deepening cycle 3."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_column_density_variance, pbm_diagonal_pixel_count
from src.python.pgm import pgm_brightness_histogram, pgm_contrast_ratio
from src.python.fodp import fodp_slide_text_variance, fodp_total_images
from src.python.fodt import fodt_paragraph_length_range, fodt_max_heading_depth

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
_FODT = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"


class TestPbmColumnDensityVariance:
    def test_returns_float(self):
        result = pbm_column_density_variance(_PBM)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = pbm_column_density_variance(_PBM)
        assert result >= 0.0


class TestPbmDiagonalPixelCount:
    def test_returns_int(self):
        result = pbm_diagonal_pixel_count(_PBM)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = pbm_diagonal_pixel_count(_PBM)
        assert result >= 0


class TestPgmBrightnessHistogram:
    def test_returns_list(self):
        result = pgm_brightness_histogram(_PGM)
        assert isinstance(result, list)

    def test_default_4_bins(self):
        result = pgm_brightness_histogram(_PGM)
        assert len(result) == 4


class TestPgmContrastRatio:
    def test_returns_float(self):
        result = pgm_contrast_ratio(_PGM)
        assert isinstance(result, float)

    def test_between_zero_and_one(self):
        result = pgm_contrast_ratio(_PGM)
        assert 0.0 <= result <= 1.0


class TestFodpSlideTextVariance:
    def test_returns_float(self):
        result = fodp_slide_text_variance(_FODP)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = fodp_slide_text_variance(_FODP)
        assert result >= 0.0


class TestFodpTotalImages:
    def test_returns_int(self):
        result = fodp_total_images(_FODP)
        assert isinstance(result, int)


class TestFodtParagraphLengthRange:
    def test_returns_int(self):
        result = fodt_paragraph_length_range(_FODT)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodt_paragraph_length_range(_FODT)
        assert result >= 0


class TestFodtMaxHeadingDepth:
    def test_returns_int(self):
        result = fodt_max_heading_depth(_FODT)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodt_max_heading_depth(_FODT)
        assert result >= 0
