"""
test_r66_ppm_advancement.py -- R66 Train I: PPM format track advancement.

New capability: ppm_channel_histogram(ppm_doc) -> dict with red/green/blue 256-bin lists

R66 Sprint: FORMAT-FACTORY-R66 product advancement
Train I -- PPM format track advancement
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_src = Path(__file__).resolve().parents[3] / "src" / "python"
sys.path.insert(0, str(_src))

from ppm.ppm_stats import ppm_channel_histogram


# ---------------------------------------------------------------------------
# ppm_channel_histogram tests
# ---------------------------------------------------------------------------

class TestPpmChannelHistogram:
    """Tests for ppm_channel_histogram()."""

    def test_empty_doc_returns_zeroed_histograms(self):
        result = ppm_channel_histogram({"pixels": []})
        assert isinstance(result, dict)
        assert len(result["red"]) == 256
        assert len(result["green"]) == 256
        assert len(result["blue"]) == 256
        assert sum(result["red"]) == 0

    def test_returns_correct_keys(self):
        result = ppm_channel_histogram({})
        assert "red" in result
        assert "green" in result
        assert "blue" in result

    def test_single_pixel_bins_correctly(self):
        doc = {"pixels": [(100, 150, 200)], "maxval": 255}
        result = ppm_channel_histogram(doc)
        assert result["red"][100] == 1
        assert result["green"][150] == 1
        assert result["blue"][200] == 1
        assert sum(result["red"]) == 1

    def test_multiple_pixels(self):
        doc = {"pixels": [(0, 0, 0), (255, 255, 255), (0, 0, 0)], "maxval": 255}
        result = ppm_channel_histogram(doc)
        assert result["red"][0] == 2
        assert result["red"][255] == 1
        assert sum(result["red"]) == 3

    def test_maxval_scaling(self):
        """Values should be scaled from maxval range to 0-255."""
        doc = {"pixels": [(511, 0, 0)], "maxval": 511}
        result = ppm_channel_histogram(doc)
        assert result["red"][255] == 1

    def test_no_pixels_key_returns_zeroed(self):
        result = ppm_channel_histogram({})
        assert sum(result["red"]) == 0
        assert sum(result["green"]) == 0
        assert sum(result["blue"]) == 0

    def test_invalid_pixel_skipped(self):
        doc = {"pixels": [(100, 200, 50), "invalid", (10, 20)], "maxval": 255}
        result = ppm_channel_histogram(doc)
        # Only the first valid pixel should be counted
        assert sum(result["red"]) == 1
