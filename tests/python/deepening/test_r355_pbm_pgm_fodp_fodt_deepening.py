"""Sprint 125 — PBM/PGM/FODP/FODT cycle 14 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_row_white_ratio, pbm_center_region_density
from src.python.pgm.pgm_parser import pgm_pixel_variance, pgm_center_pixel_value
from src.python.fodp.fodp_codec import fodp_max_shape_count_per_slide, fodp_total_image_count
from src.python.fodt.neutral_model import fodt_min_paragraph_text_length, fodt_paragraph_text_sum

_PBM = next((_REPO / "samples" / "by-format" / "pbm" / "valid").glob("*.pbm"))
_PGM = next((_REPO / "samples" / "by-format" / "pgm" / "valid").glob("*.pgm"))
_FODP = next((_REPO / "samples" / "by-format" / "fodp").glob("*.fodp"))
_FODT = next((_REPO / "samples" / "by-format" / "fodt").glob("*.fodt"))


class TestPbmRowWhiteRatio:
    def test_returns_float(self):
        assert isinstance(pbm_row_white_ratio(_PBM), float)

    def test_range(self):
        assert 0.0 <= pbm_row_white_ratio(_PBM) <= 1.0


class TestPbmCenterRegionDensity:
    def test_returns_float(self):
        assert isinstance(pbm_center_region_density(_PBM), float)

    def test_range(self):
        assert 0.0 <= pbm_center_region_density(_PBM) <= 1.0


class TestPgmPixelVariance:
    def test_returns_float(self):
        assert isinstance(pgm_pixel_variance(_PGM), float)

    def test_non_negative(self):
        assert pgm_pixel_variance(_PGM) >= 0.0


class TestPgmCenterPixelValue:
    def test_returns_int(self):
        assert isinstance(pgm_center_pixel_value(_PGM), int)

    def test_non_negative(self):
        assert pgm_center_pixel_value(_PGM) >= 0


class TestFodpMaxShapeCountPerSlide:
    def test_returns_int(self):
        assert isinstance(fodp_max_shape_count_per_slide(_FODP), int)

    def test_non_negative(self):
        assert fodp_max_shape_count_per_slide(_FODP) >= 0


class TestFodpTotalImageCount:
    def test_returns_int(self):
        assert isinstance(fodp_total_image_count(_FODP), int)

    def test_non_negative(self):
        assert fodp_total_image_count(_FODP) >= 0


class TestFodtMinParagraphTextLength:
    def test_returns_int(self):
        assert isinstance(fodt_min_paragraph_text_length(_FODT), int)

    def test_non_negative(self):
        assert fodt_min_paragraph_text_length(_FODT) >= 0


class TestFodtParagraphTextSum:
    def test_returns_int(self):
        assert isinstance(fodt_paragraph_text_sum(_FODT), int)

    def test_non_negative(self):
        assert fodt_paragraph_text_sum(_FODT) >= 0
