"""Tests for pgm_to_ppm dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm"
from src.python.pgm.pgm_to_ppm import convert_pgm_to_ppm, pgm_pixels_to_ppm_pixels


class TestPgmToPpmBasic:
    def test_returns_dict(self, tmp_path):
        dest = tmp_path / "out.ppm"
        result = convert_pgm_to_ppm(MINIMAL_PGM, dest)
        assert isinstance(result, dict)

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.ppm"
        convert_pgm_to_ppm(MINIMAL_PGM, dest)
        assert dest.exists()

    def test_result_has_dimensions(self, tmp_path):
        dest = tmp_path / "out.ppm"
        result = convert_pgm_to_ppm(MINIMAL_PGM, dest)
        assert "width" in result and "height" in result

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.ppm"
        convert_pgm_to_ppm(MINIMAL_PGM, dest)
        assert dest.stat().st_size > 0


class TestPgmPixelsToPpmPixels:
    def test_gray_maps_to_rgb_triple(self):
        result = pgm_pixels_to_ppm_pixels([128], maxval=255)
        assert result == [(128, 128, 128)]

    def test_zero_maps_to_black(self):
        result = pgm_pixels_to_ppm_pixels([0])
        assert result == [(0, 0, 0)]

    def test_length_preserved(self):
        pixels = [0, 64, 128, 255]
        result = pgm_pixels_to_ppm_pixels(pixels)
        assert len(result) == 4
