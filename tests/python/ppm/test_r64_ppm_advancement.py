"""
test_r64_ppm_advancement.py -- R64 Train I: PPM format track advancement.

New capability: ppm_brightness_histogram(ppm_doc, bins=4)
  Returns dict mapping bin labels to pixel counts based on brightness.

R64 Sprint: Train I -- PPM format track advancement
"""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from src.python.ppm.ppm_stats import ppm_brightness_histogram


def _doc(pixels, maxval=255):
    return {"pixels": pixels, "maxval": maxval}


class TestPpmBrightnessHistogram:
    def test_empty_pixels(self):
        result = ppm_brightness_histogram({"pixels": []})
        assert result == {}

    def test_single_black_pixel(self):
        result = ppm_brightness_histogram(_doc([(0, 0, 0)]))
        # bins=4 default: 0-63, 64-127, 128-191, 192-255
        assert sum(result.values()) == 1
        # brightness=0 should be in first bin
        first_bin = list(result.keys())[0]
        assert result[first_bin] == 1

    def test_single_white_pixel(self):
        result = ppm_brightness_histogram(_doc([(255, 255, 255)]))
        assert sum(result.values()) == 1
        # brightness=255 should be in last bin
        last_bin = list(result.keys())[-1]
        assert result[last_bin] == 1

    def test_all_bins_populated(self):
        pixels = [
            (0, 0, 0),        # brightness 0 -> bin 0
            (90, 90, 90),     # brightness 90 -> bin 1
            (160, 160, 160),  # brightness 160 -> bin 2
            (250, 250, 250),  # brightness 250 -> bin 3
        ]
        result = ppm_brightness_histogram(_doc(pixels))
        assert sum(result.values()) == 4
        values = list(result.values())
        assert all(v >= 1 for v in values)

    def test_custom_bins(self):
        pixels = [(128, 128, 128)]
        result = ppm_brightness_histogram(_doc(pixels), bins=2)
        assert len(result) == 2
        assert sum(result.values()) == 1

    def test_four_bins_correct_labels(self):
        result = ppm_brightness_histogram(_doc([(0, 0, 0)]), bins=4)
        keys = list(result.keys())
        assert len(keys) == 4
        # First bin starts at 0, last bin ends at 255
        assert keys[0].startswith("0-")
        assert keys[-1].endswith("255")

    def test_multiple_pixels_same_bin(self):
        pixels = [(10, 10, 10), (20, 20, 20), (30, 30, 30)]
        result = ppm_brightness_histogram(_doc(pixels), bins=4)
        first_bin = list(result.keys())[0]
        assert result[first_bin] == 3

    def test_callable_from_module(self):
        from src.python.ppm import ppm_stats
        assert callable(ppm_stats.ppm_brightness_histogram)
