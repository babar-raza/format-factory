# R94 Train Q: PPM/PGM Grayscale Conversion Hardening Tests
# Governed skill: /verify-dogfood-path
# Ledger: R94-GOVERNED-PYTHON-NETPBM-GRAYSCALE-CONVERSION-001
# Sprint: FORMAT-FACTORY-R94-CONTEXT-PACK-SELF-CONTAINED-DECLARATION-REVIEW-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

"""Tests for PPM-to-PGM grayscale conversion edge cases."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))

from ppm.ppm_to_pgm import ppm_pixels_to_pgm_pixels
from pgm.pgm_parser import write_pgm, parse_pgm


class TestPpmGrayscaleConversion:
    """R94 PPM→PGM conversion edge cases."""

    def test_pure_red_produces_nonzero_gray(self):
        """Pure red (255,0,0) should produce non-zero grayscale via luminance."""
        pixels = [(255, 0, 0)]
        gray = ppm_pixels_to_pgm_pixels(pixels)
        assert gray[0] > 0, "Pure red should have non-zero luminance"
        assert gray[0] < 255, "Pure red should not be full white"

    def test_pure_green_produces_higher_than_red(self):
        """Green has highest luminance weight in standard formula."""
        red_gray = ppm_pixels_to_pgm_pixels([(255, 0, 0)])[0]
        green_gray = ppm_pixels_to_pgm_pixels([(0, 255, 0)])[0]
        assert green_gray > red_gray, "Green should have higher luminance than red"

    def test_pure_white_produces_max(self):
        """(255,255,255) should produce 255 or very close."""
        gray = ppm_pixels_to_pgm_pixels([(255, 255, 255)])
        assert gray[0] >= 254, f"White should produce ~255, got {gray[0]}"

    def test_pure_black_produces_zero(self):
        """(0,0,0) should produce 0."""
        gray = ppm_pixels_to_pgm_pixels([(0, 0, 0)])
        assert gray[0] == 0

    def test_roundtrip_file_write_read(self, tmp_path):
        """Write a PGM from converted PPM data and read it back."""
        pixels = [(100, 150, 200), (50, 50, 50), (200, 100, 50), (0, 255, 0)]
        gray_pixels = ppm_pixels_to_pgm_pixels(pixels)
        pgm_path = tmp_path / "test.pgm"
        write_pgm(
            file_path=str(pgm_path),
            width=2,
            height=2,
            pixels=gray_pixels,
            maxval=255,
        )
        doc = parse_pgm(str(pgm_path))
        assert doc["width"] == 2
        assert doc["height"] == 2
        assert doc["pixel_count"] == 4

    def test_single_pixel_conversion(self, tmp_path):
        """1x1 image round-trips through file."""
        pixels = [(128, 128, 128)]
        gray = ppm_pixels_to_pgm_pixels(pixels)
        pgm_path = tmp_path / "single.pgm"
        write_pgm(file_path=str(pgm_path), width=1, height=1, pixels=gray, maxval=255)
        doc = parse_pgm(str(pgm_path))
        assert doc["pixel_count"] == 1
        assert doc["ok"] is True

    def test_empty_pixel_list(self):
        """Empty pixel list produces empty gray list."""
        gray = ppm_pixels_to_pgm_pixels([])
        assert gray == []

    def test_luminance_range(self):
        """All possible single-channel max values produce gray in [0,255]."""
        for r in [0, 128, 255]:
            for g in [0, 128, 255]:
                for b in [0, 128, 255]:
                    gray = ppm_pixels_to_pgm_pixels([(r, g, b)])
                    assert 0 <= gray[0] <= 255, f"Out of range for ({r},{g},{b}): {gray[0]}"
