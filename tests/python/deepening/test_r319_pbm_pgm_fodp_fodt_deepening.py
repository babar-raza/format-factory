"""Sprint 89 — PBM/PGM/FODP/FODT cycle 5: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_border_density, pbm_row_black_variance
from src.python.pgm.pgm_parser import pgm_bright_pixel_count, pgm_brightness_variance
from src.python.fodp.fodp_codec import fodp_longest_slide_text_length, fodp_notes_total_length
from src.python.fodt.neutral_model import fodt_list_item_count, fodt_inline_count

_PBM = _REPO / "samples" / "by-format" / "pbm" / "valid"
_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"
_FODP = _REPO / "samples" / "by-format" / "fodp"
_FODT = _REPO / "samples" / "by-format" / "fodt"


@pytest.fixture
def pbm_sample():
    return next(_PBM.glob("*.pbm"))


@pytest.fixture
def pgm_sample():
    return next(_PGM.glob("*.pgm"))


@pytest.fixture
def fodp_sample():
    return next(_FODP.glob("*.fodp"))


@pytest.fixture
def fodt_sample():
    return next(_FODT.glob("*.fodt"))


# --- PBM ---
class TestPbmBorderDensity:
    def test_returns_float(self, pbm_sample):
        result = pbm_border_density(pbm_sample)
        assert isinstance(result, float)

    def test_between_zero_and_one(self, pbm_sample):
        result = pbm_border_density(pbm_sample)
        assert 0.0 <= result <= 1.0


class TestPbmRowBlackVariance:
    def test_returns_float(self, pbm_sample):
        result = pbm_row_black_variance(pbm_sample)
        assert isinstance(result, float)

    def test_non_negative(self, pbm_sample):
        assert pbm_row_black_variance(pbm_sample) >= 0.0


# --- PGM ---
class TestPgmBrightPixelCount:
    def test_returns_int(self, pgm_sample):
        result = pgm_bright_pixel_count(pgm_sample)
        assert isinstance(result, int)

    def test_non_negative(self, pgm_sample):
        assert pgm_bright_pixel_count(pgm_sample) >= 0


class TestPgmBrightnessVariance:
    def test_returns_float(self, pgm_sample):
        result = pgm_brightness_variance(pgm_sample)
        assert isinstance(result, float)

    def test_non_negative(self, pgm_sample):
        assert pgm_brightness_variance(pgm_sample) >= 0.0


# --- FODP ---
class TestFodpLongestSlideTextLength:
    def test_returns_int(self, fodp_sample):
        result = fodp_longest_slide_text_length(fodp_sample)
        assert isinstance(result, int)

    def test_non_negative(self, fodp_sample):
        assert fodp_longest_slide_text_length(fodp_sample) >= 0


class TestFodpNotesTotalLength:
    def test_returns_int(self, fodp_sample):
        result = fodp_notes_total_length(fodp_sample)
        assert isinstance(result, int)

    def test_non_negative(self, fodp_sample):
        assert fodp_notes_total_length(fodp_sample) >= 0


# --- FODT ---
class TestFodtListItemCount:
    def test_returns_int(self, fodt_sample):
        result = fodt_list_item_count(fodt_sample)
        assert isinstance(result, int)

    def test_non_negative(self, fodt_sample):
        assert fodt_list_item_count(fodt_sample) >= 0


class TestFodtInlineCount:
    def test_returns_int(self, fodt_sample):
        result = fodt_inline_count(fodt_sample)
        assert isinstance(result, int)

    def test_non_negative(self, fodt_sample):
        assert fodt_inline_count(fodt_sample) >= 0
