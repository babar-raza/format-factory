"""
test_r155_pbm_crop.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT13-001
Added: 2026-06-09

Tests for PBM crop function.
Authority: P5 (SAL-PBM-00001, SAL-PBM-00002)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import crop, write_pbm, parse_pbm_strict, PbmError


def _make_pbm(tmp_path: Path, width: int, height: int, pixels: list[int]) -> Path:
    p = tmp_path / "source.pbm"
    write_pbm(pixels, width, height, p)
    return p


class TestCrop:
    """crop: extract a rectangular region from a PBM image."""

    def test_crop_full_image(self, tmp_path):
        pixels = [0, 1, 1, 0]
        src = _make_pbm(tmp_path, 2, 2, pixels)
        dst = tmp_path / "cropped.pbm"
        result = crop(src, dst, 0, 0, 2, 2)
        assert result["ok"] is True
        img = parse_pbm_strict(dst)
        assert img.pixels == pixels

    def test_crop_top_left(self, tmp_path):
        # 3x3 image, crop 2x2 from top-left
        pixels = [0, 1, 0,
                  1, 1, 0,
                  0, 0, 1]
        src = _make_pbm(tmp_path, 3, 3, pixels)
        dst = tmp_path / "tl.pbm"
        result = crop(src, dst, 0, 0, 2, 2)
        assert result["width"] == 2
        assert result["height"] == 2
        img = parse_pbm_strict(dst)
        assert img.pixels == [0, 1, 1, 1]

    def test_crop_bottom_right(self, tmp_path):
        pixels = [0, 1, 0,
                  1, 1, 0,
                  0, 0, 1]
        src = _make_pbm(tmp_path, 3, 3, pixels)
        dst = tmp_path / "br.pbm"
        crop(src, dst, 1, 1, 2, 2)
        img = parse_pbm_strict(dst)
        assert img.pixels == [1, 0, 0, 1]

    def test_crop_single_pixel(self, tmp_path):
        pixels = [0, 1, 1, 0]
        src = _make_pbm(tmp_path, 2, 2, pixels)
        dst = tmp_path / "single.pbm"
        crop(src, dst, 1, 0, 1, 1)
        img = parse_pbm_strict(dst)
        assert img.pixels == [1]

    def test_crop_out_of_bounds_raises(self, tmp_path):
        pixels = [0, 1, 1, 0]
        src = _make_pbm(tmp_path, 2, 2, pixels)
        with pytest.raises(ValueError):
            crop(src, tmp_path / "bad.pbm", 1, 1, 2, 2)

    def test_crop_negative_raises(self, tmp_path):
        pixels = [0, 1, 1, 0]
        src = _make_pbm(tmp_path, 2, 2, pixels)
        with pytest.raises(ValueError):
            crop(src, tmp_path / "bad.pbm", -1, 0, 1, 1)

    def test_crop_nonexistent_source_raises(self, tmp_path):
        with pytest.raises(PbmError):
            crop(tmp_path / "ghost.pbm", tmp_path / "out.pbm", 0, 0, 1, 1)
