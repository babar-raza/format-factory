"""Tests for pbm_black_pixel_ratio and pbm_dimensions.

Product deepening: PBM analytics — TC-H3-002-PBM / PDC-PBM-RATIO-DIMS-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import write_pbm, pbm_black_pixel_ratio, pbm_dimensions


def _make_pbm(tmp_path, name, w, h, pixels):
    p = tmp_path / f"{name}.pbm"
    write_pbm(pixels, w, h, str(p))
    return p


class TestPbmBlackPixelRatio:
    def test_all_black(self, tmp_path):
        p = _make_pbm(tmp_path, "allblk", 2, 2, [1, 1, 1, 1])
        assert pbm_black_pixel_ratio(p) == 1.0

    def test_half_black(self, tmp_path):
        p = _make_pbm(tmp_path, "half", 2, 2, [1, 0, 1, 0])
        assert pbm_black_pixel_ratio(p) == 0.5

    def test_all_white(self, tmp_path):
        p = _make_pbm(tmp_path, "allwht", 2, 2, [0, 0, 0, 0])
        assert pbm_black_pixel_ratio(p) == 0.0

    def test_returns_float(self, tmp_path):
        p = _make_pbm(tmp_path, "ft", 1, 1, [1])
        assert isinstance(pbm_black_pixel_ratio(p), float)

    def test_bounded(self, tmp_path):
        p = _make_pbm(tmp_path, "bound", 2, 1, [1, 0])
        r = pbm_black_pixel_ratio(p)
        assert 0.0 <= r <= 1.0


class TestPbmDimensions:
    def test_small(self, tmp_path):
        p = _make_pbm(tmp_path, "small", 3, 2, [0, 1, 0, 1, 0, 1])
        d = pbm_dimensions(p)
        assert d["width"] == 3
        assert d["height"] == 2

    def test_square(self, tmp_path):
        p = _make_pbm(tmp_path, "sq", 4, 4, [0] * 16)
        d = pbm_dimensions(p)
        assert d["width"] == d["height"] == 4

    def test_returns_dict(self, tmp_path):
        p = _make_pbm(tmp_path, "dict_t", 1, 1, [0])
        d = pbm_dimensions(p)
        assert isinstance(d, dict)
        assert "width" in d and "height" in d

    def test_single_pixel(self, tmp_path):
        p = _make_pbm(tmp_path, "one_px", 1, 1, [1])
        d = pbm_dimensions(p)
        assert d["width"] == 1 and d["height"] == 1

    def test_wide(self, tmp_path):
        p = _make_pbm(tmp_path, "wide", 5, 1, [0, 1, 0, 1, 0])
        d = pbm_dimensions(p)
        assert d["width"] == 5 and d["height"] == 1
