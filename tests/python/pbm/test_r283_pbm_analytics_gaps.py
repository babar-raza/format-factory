"""
Tests for PBM analytics gap closure (2 FOSS gaps).
Closes: GAP-PBM-FOSS-PBM_AVG_RO-001, GAP-PBM-FOSS-PBM_BORDER-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_avg_row_density,
    pbm_border_black_count,
)

_PBM_1x1 = _REPO / "samples/by-format/pbm/valid/1x1-black.pbm"
_PBM_2x2 = _REPO / "samples/by-format/pbm/valid/2x2-checker.pbm"
_PBM_3x2 = _REPO / "samples/by-format/pbm/valid/3x2-pattern.pbm"


class TestPbmAvgRowDensity:
    def test_returns_float(self):
        assert isinstance(pbm_avg_row_density(_PBM_1x1), float)

    def test_nonnegative(self):
        assert pbm_avg_row_density(_PBM_1x1) >= 0.0

    def test_at_most_one(self):
        # density is a ratio; max is 1.0
        assert pbm_avg_row_density(_PBM_2x2) <= 1.0

    def test_all_black_pixel_density_is_one(self):
        # 1x1-black.pbm single black pixel → density == 1.0
        assert pbm_avg_row_density(_PBM_1x1) == pytest.approx(1.0)


class TestPbmBorderBlackCount:
    def test_returns_int(self):
        assert isinstance(pbm_border_black_count(_PBM_1x1), int)

    def test_nonnegative(self):
        assert pbm_border_black_count(_PBM_1x1) >= 0

    def test_single_black_pixel_border_count_is_one(self):
        # 1x1-black.pbm: the single pixel is on the border and is black
        assert pbm_border_black_count(_PBM_1x1) == 1

    def test_larger_image_border_nonnegative(self):
        assert pbm_border_black_count(_PBM_3x2) >= 0
