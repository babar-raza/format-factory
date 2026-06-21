"""Sprint R290E: PBM analytics deepening — row_black_density, column_black_density, border_pixel_count."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_row_black_density,
    pbm_column_black_density,
    pbm_border_pixel_count,
)

SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"
BLACK_1x1 = SAMPLES / "1x1-black.pbm"
CHECKER = SAMPLES / "2x2-checker.pbm"
PATTERN = SAMPLES / "3x2-pattern.pbm"


@pytest.fixture
def black_sample():
    if not BLACK_1x1.exists():
        pytest.skip("PBM black sample not available")
    return BLACK_1x1


@pytest.fixture
def checker_sample():
    if not CHECKER.exists():
        pytest.skip("PBM checker sample not available")
    return CHECKER


class TestPbmRowBlackDensity:
    def test_returns_float(self, black_sample):
        assert isinstance(pbm_row_black_density(black_sample), float)

    def test_all_black_is_one(self, black_sample):
        assert pbm_row_black_density(black_sample) == 1.0

    def test_nonnegative(self, checker_sample):
        assert pbm_row_black_density(checker_sample) >= 0.0


class TestPbmColumnBlackDensity:
    def test_returns_float(self, black_sample):
        assert isinstance(pbm_column_black_density(black_sample), float)

    def test_nonnegative(self, checker_sample):
        assert pbm_column_black_density(checker_sample) >= 0.0


class TestPbmBorderPixelCount:
    def test_returns_int(self, black_sample):
        assert isinstance(pbm_border_pixel_count(black_sample), int)

    def test_1x1_black_border_is_one(self, black_sample):
        assert pbm_border_pixel_count(black_sample) == 1

    def test_nonnegative(self, checker_sample):
        assert pbm_border_pixel_count(checker_sample) >= 0
