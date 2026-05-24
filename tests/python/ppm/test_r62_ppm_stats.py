"""
test_r62_ppm_stats.py — R62 Train I: PPM stats API tests.

Tests the two new capability functions added to src/python/ppm/ppm_stats.py:
  - image_stats(): image dimensions, aspect ratio, megapixels, depth
  - image_color_sample(): pixel sample metadata

R62 Sprint: FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from ppm.ppm_stats import image_stats, image_color_sample


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ppm_doc(width=0, height=0, maxval=255, magic="P3", pixel_count=None):
    if pixel_count is None:
        pixel_count = width * height
    return {
        "ok": True,
        "width": width,
        "height": height,
        "maxval": maxval,
        "magic": magic,
        "pixel_count": pixel_count,
    }


# ---------------------------------------------------------------------------
# image_stats
# ---------------------------------------------------------------------------

class TestImageStatsEmpty:
    def test_zero_size_image(self):
        result = image_stats(_ppm_doc())
        assert result["width"] == 0
        assert result["height"] == 0
        assert result["pixel_count"] == 0

    def test_aspect_ratio_none_when_height_zero(self):
        result = image_stats(_ppm_doc(width=100, height=0))
        assert result["aspect_ratio"] is None

    def test_returns_dict(self):
        assert isinstance(image_stats(_ppm_doc()), dict)

    def test_has_required_keys(self):
        result = image_stats(_ppm_doc(4, 4))
        for key in ("width", "height", "pixel_count", "maxval", "magic",
                    "depth", "aspect_ratio", "megapixels"):
            assert key in result, f"Missing key: {key}"


class TestImageStatsDimensions:
    def test_1x1_image(self):
        result = image_stats(_ppm_doc(1, 1))
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["pixel_count"] == 1

    def test_square_aspect_ratio(self):
        result = image_stats(_ppm_doc(100, 100))
        assert result["aspect_ratio"] == 1.0

    def test_wide_aspect_ratio(self):
        result = image_stats(_ppm_doc(200, 100))
        assert result["aspect_ratio"] == 2.0

    def test_tall_image_aspect_ratio_less_than_1(self):
        result = image_stats(_ppm_doc(100, 200))
        assert result["aspect_ratio"] == 0.5

    def test_megapixels_calculation(self):
        result = image_stats(_ppm_doc(1000, 1000))
        assert abs(result["megapixels"] - 1.0) < 0.01

    def test_pixel_count_preserved(self):
        result = image_stats(_ppm_doc(4, 3))
        assert result["pixel_count"] == 12


class TestImageStatsDepth:
    def test_8bit_depth_maxval_255(self):
        result = image_stats(_ppm_doc(10, 10, maxval=255))
        assert result["depth"] == "8-bit"

    def test_16bit_depth_maxval_65535(self):
        result = image_stats(_ppm_doc(10, 10, maxval=65535))
        assert result["depth"] == "16-bit"

    def test_16bit_depth_maxval_256(self):
        result = image_stats(_ppm_doc(10, 10, maxval=256))
        assert result["depth"] == "16-bit"

    def test_8bit_depth_maxval_1(self):
        result = image_stats(_ppm_doc(10, 10, maxval=1))
        assert result["depth"] == "8-bit"

    def test_magic_preserved(self):
        result = image_stats(_ppm_doc(4, 4, magic="P6"))
        assert result["magic"] == "P6"

    def test_maxval_preserved(self):
        result = image_stats(_ppm_doc(4, 4, maxval=1023))
        assert result["maxval"] == 1023


# ---------------------------------------------------------------------------
# image_color_sample
# ---------------------------------------------------------------------------

class TestImageColorSample:
    def test_returns_dict(self):
        assert isinstance(image_color_sample(_ppm_doc()), dict)

    def test_has_required_keys(self):
        result = image_color_sample(_ppm_doc(4, 4))
        for key in ("total_pixels", "sample_size", "note"):
            assert key in result, f"Missing key: {key}"

    def test_total_pixels_matches(self):
        result = image_color_sample(_ppm_doc(10, 10))
        assert result["total_pixels"] == 100

    def test_sample_size_capped_at_total(self):
        result = image_color_sample(_ppm_doc(2, 2), sample_size=100)
        assert result["sample_size"] <= 4

    def test_note_field_is_string(self):
        result = image_color_sample(_ppm_doc(4, 4))
        assert isinstance(result["note"], str)
