"""
Sprint ff-idempotent-spec-to-feature-swarm-20260617 — Netpbm analytics deepening.
Tests for eighty_nine variants in PBM, PGM, PPM.
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_total_pixels_times_eighty_nine, pbm_file_size_bytes_times_eighty_nine
from src.python.pgm import pgm_total_pixel_count_times_eighty_nine, pgm_file_size_bytes_times_eighty_nine
from src.python.ppm import ppm_file_size_bytes_times_eighty_nine, ppm_unique_pixel_count_times_eighty_nine

_PBM = str(_REPO / "samples/by-format/pbm/valid/1x1-black.pbm")
_PBM2 = str(_REPO / "samples/by-format/pbm/valid/2x2-checker.pbm")
_PGM = str(_REPO / "samples/by-format/pgm/valid/1x1-white.pgm")
_PGM2 = str(_REPO / "samples/by-format/pgm/valid/2x2-gradient.pgm")
_PPM = str(_REPO / "samples/by-format/ppm/valid/1x1-red.ppm")
_PPM2 = str(_REPO / "samples/by-format/ppm/valid/2x2-rgbw.ppm")


class TestPbmTotalPixelsTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(pbm_total_pixels_times_eighty_nine(_PBM), int)
    def test_non_negative(self):
        assert pbm_total_pixels_times_eighty_nine(_PBM) >= 0
    def test_divisible_by_89(self):
        assert pbm_total_pixels_times_eighty_nine(_PBM) % 89 == 0
    def test_2x2_gte_1x1(self):
        assert pbm_total_pixels_times_eighty_nine(_PBM2) >= pbm_total_pixels_times_eighty_nine(_PBM)


class TestPbmFileSizeBytesTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(pbm_file_size_bytes_times_eighty_nine(_PBM), int)
    def test_positive(self):
        assert pbm_file_size_bytes_times_eighty_nine(_PBM) > 0
    def test_divisible_by_89(self):
        assert pbm_file_size_bytes_times_eighty_nine(_PBM) % 89 == 0


class TestPgmTotalPixelCountTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(pgm_total_pixel_count_times_eighty_nine(_PGM), int)
    def test_non_negative(self):
        assert pgm_total_pixel_count_times_eighty_nine(_PGM) >= 0
    def test_divisible_by_89(self):
        assert pgm_total_pixel_count_times_eighty_nine(_PGM) % 89 == 0
    def test_2x2_gte_1x1(self):
        assert pgm_total_pixel_count_times_eighty_nine(_PGM2) >= pgm_total_pixel_count_times_eighty_nine(_PGM)


class TestPgmFileSizeBytesTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(pgm_file_size_bytes_times_eighty_nine(_PGM), int)
    def test_positive(self):
        assert pgm_file_size_bytes_times_eighty_nine(_PGM) > 0
    def test_divisible_by_89(self):
        assert pgm_file_size_bytes_times_eighty_nine(_PGM) % 89 == 0


class TestPpmFileSizeBytesTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_bytes_times_eighty_nine(_PPM), int)
    def test_positive(self):
        assert ppm_file_size_bytes_times_eighty_nine(_PPM) > 0
    def test_divisible_by_89(self):
        assert ppm_file_size_bytes_times_eighty_nine(_PPM) % 89 == 0


class TestPpmUniquePixelCountTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(ppm_unique_pixel_count_times_eighty_nine(_PPM), int)
    def test_non_negative(self):
        assert ppm_unique_pixel_count_times_eighty_nine(_PPM) >= 0
    def test_divisible_by_89(self):
        assert ppm_unique_pixel_count_times_eighty_nine(_PPM) % 89 == 0
    def test_2x2_gte_1x1(self):
        assert ppm_unique_pixel_count_times_eighty_nine(_PPM2) >= ppm_unique_pixel_count_times_eighty_nine(_PPM)
