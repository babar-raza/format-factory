"""Sprint 93 — PBM/PGM/FODP/FODT cycle 6: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm.pbm_parser import pbm_corner_black_count, pbm_row_uniformity
from src.python.pgm.pgm_parser import pgm_entropy, pgm_mode_pixel_value
from src.python.fodp.fodp_codec import fodp_word_count, fodp_shape_diversity
from src.python.fodt.neutral_model import fodt_punctuation_count, fodt_paragraph_variance

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
class TestPbmCornerBlackCount:
    def test_returns_int(self, pbm_sample):
        result = pbm_corner_black_count(pbm_sample)
        assert isinstance(result, int)

    def test_bounded(self, pbm_sample):
        result = pbm_corner_black_count(pbm_sample)
        assert 0 <= result <= 4


class TestPbmRowUniformity:
    def test_returns_float(self, pbm_sample):
        result = pbm_row_uniformity(pbm_sample)
        assert isinstance(result, float)

    def test_between_zero_and_one(self, pbm_sample):
        result = pbm_row_uniformity(pbm_sample)
        assert 0.0 <= result <= 1.0


# --- PGM ---
class TestPgmEntropy:
    def test_returns_float(self, pgm_sample):
        result = pgm_entropy(pgm_sample)
        assert isinstance(result, float)

    def test_non_negative(self, pgm_sample):
        assert pgm_entropy(pgm_sample) >= 0.0


class TestPgmModePixelValue:
    def test_returns_int(self, pgm_sample):
        result = pgm_mode_pixel_value(pgm_sample)
        assert isinstance(result, int)

    def test_non_negative(self, pgm_sample):
        assert pgm_mode_pixel_value(pgm_sample) >= 0


# --- FODP ---
class TestFodpWordCount:
    def test_returns_int(self, fodp_sample):
        result = fodp_word_count(fodp_sample)
        assert isinstance(result, int)

    def test_non_negative(self, fodp_sample):
        assert fodp_word_count(fodp_sample) >= 0


class TestFodpShapeDiversity:
    def test_returns_int(self, fodp_sample):
        result = fodp_shape_diversity(fodp_sample)
        assert isinstance(result, int)

    def test_non_negative(self, fodp_sample):
        assert fodp_shape_diversity(fodp_sample) >= 0


# --- FODT ---
class TestFodtPunctuationCount:
    def test_returns_int(self, fodt_sample):
        result = fodt_punctuation_count(fodt_sample)
        assert isinstance(result, int)

    def test_non_negative(self, fodt_sample):
        assert fodt_punctuation_count(fodt_sample) >= 0


class TestFodtParagraphVariance:
    def test_returns_float(self, fodt_sample):
        result = fodt_paragraph_variance(fodt_sample)
        assert isinstance(result, float)

    def test_non_negative(self, fodt_sample):
        assert fodt_paragraph_variance(fodt_sample) >= 0.0
