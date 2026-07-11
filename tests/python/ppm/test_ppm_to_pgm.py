"""Tests for ppm_to_pgm dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid" / "2x2-rgbw.ppm"
from src.python.ppm.ppm_to_pgm import convert_ppm_to_pgm, ppm_pixels_to_pgm_pixels


class TestPpmToPgmBasic:
    def test_returns_dict(self, tmp_path):
        dest = tmp_path / "out.pgm"
        result = convert_ppm_to_pgm(MINIMAL_PPM, dest)
        assert isinstance(result, dict)

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.pgm"
        convert_ppm_to_pgm(MINIMAL_PPM, dest)
        assert dest.exists()

    def test_result_has_dimensions(self, tmp_path):
        dest = tmp_path / "out.pgm"
        result = convert_ppm_to_pgm(MINIMAL_PPM, dest)
        assert "width" in result and "height" in result

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.pgm"
        convert_ppm_to_pgm(MINIMAL_PPM, dest)
        assert dest.stat().st_size > 0


class TestPpmPixelsToPgmPixels:
    def test_black_maps_to_zero(self):
        result = ppm_pixels_to_pgm_pixels([(0, 0, 0)], maxval=255)
        assert result == [0]

    def test_white_maps_to_bright(self):
        result = ppm_pixels_to_pgm_pixels([(255, 255, 255)], maxval=255)
        assert result[0] > 200

    def test_length_preserved(self):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        result = ppm_pixels_to_pgm_pixels(pixels, maxval=255)
        assert len(result) == 3
