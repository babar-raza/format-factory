"""Tests for pbm_row_white_ratio and pbm_center_region_density — closing GAP-PBM-FOSS-PBM_ROW_WHIT-001 and GAP-PBM-FOSS-PBM_CENTER_R-001."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import pbm_row_white_ratio, pbm_center_region_density

SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"


def test_row_white_ratio_returns_float():
    result = pbm_row_white_ratio(SAMPLES / "2x2-checker.pbm")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_row_white_ratio_1x1():
    result = pbm_row_white_ratio(SAMPLES / "1x1-black.pbm")
    assert isinstance(result, float)


def test_row_white_ratio_3x2():
    result = pbm_row_white_ratio(SAMPLES / "3x2-pattern.pbm")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_center_region_density_returns_float():
    result = pbm_center_region_density(SAMPLES / "3x2-pattern.pbm")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_center_region_density_checker():
    result = pbm_center_region_density(SAMPLES / "2x2-checker.pbm")
    assert isinstance(result, float)


def test_center_region_density_1x1():
    # 1x1 is < 2 in both dims, should return 0.0
    result = pbm_center_region_density(SAMPLES / "1x1-black.pbm")
    assert result == 0.0
