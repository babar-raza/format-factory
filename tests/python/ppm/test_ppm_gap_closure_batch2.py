"""Gap closure tests for PPM — batch 2, covering 2 remaining open gaps.

Gaps: GAP-PPM-FOSS-CONVERT_PPM_-001, GAP-PPM-FOSS-PPM_PIXELS_T-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm import (
    convert_ppm_to_pgm,
    ppm_pixels_to_pgm_pixels,
    write_ppm,
)


@pytest.fixture
def ppm_file(tmp_path):
    pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
    f = tmp_path / "test.ppm"
    write_ppm(pixels, 2, 2, 255, str(f))
    return f


# --- GAP-PPM-FOSS-CONVERT_PPM_-001 ---
class TestConvertPpmToPgm:
    def test_creates_pgm(self, ppm_file, tmp_path):
        dest = tmp_path / "out.pgm"
        result = convert_ppm_to_pgm(str(ppm_file), str(dest))
        assert dest.exists()
        assert isinstance(result, dict)
        assert result["status"] == "success"

    def test_dimensions_preserved(self, ppm_file, tmp_path):
        dest = tmp_path / "out.pgm"
        result = convert_ppm_to_pgm(str(ppm_file), str(dest))
        assert result["width"] == 2
        assert result["height"] == 2


# --- GAP-PPM-FOSS-PPM_PIXELS_T-001 ---
class TestPpmPixelsToPgmPixels:
    def test_returns_list(self):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        result = ppm_pixels_to_pgm_pixels(pixels)
        assert isinstance(result, list)
        assert len(result) == 4

    def test_grayscale_values(self):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        result = ppm_pixels_to_pgm_pixels(pixels)
        # Standard luminance: R*0.299 + G*0.587 + B*0.114
        assert result[0] == 76   # red
        assert result[1] == 150  # green
        assert result[2] == 29   # blue
        assert result[3] == 128  # gray
