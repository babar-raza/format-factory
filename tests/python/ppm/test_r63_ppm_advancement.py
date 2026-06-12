"""
test_r63_ppm_advancement.py — R63 Train I: PPM format track advancement.

New capability: ppm_channel_stats(ppm_doc)
  Returns per-channel (R, G, B) min/max/mean statistics from pixel sample.

R63 Sprint: FORMAT-FACTORY-R63-AI-ASSISTED-RC-CLOSURE-AND-WORKAHEAD-MULTI-SPRINT-MEGA-TRAIN-001
Train I — PPM format track advancement
"""
from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from src.python.ppm.ppm_stats import ppm_channel_stats


def _doc(pixels, width=None, height=None):
    doc = {"pixels": pixels}
    if width is not None:
        doc["width"] = width
    if height is not None:
        doc["height"] = height
    return doc


class TestPpmChannelStats:
    def test_empty_pixels(self):
        result = ppm_channel_stats({"pixels": []})
        assert result["total_pixels"] == 0
        assert result["per_channel"]["R"]["min"] is None

    def test_single_pixel(self):
        result = ppm_channel_stats(_doc([(255, 0, 128)]))
        assert result["total_pixels"] == 1
        assert result["per_channel"]["R"]["min"] == 255
        assert result["per_channel"]["R"]["max"] == 255
        assert result["per_channel"]["G"]["min"] == 0
        assert result["per_channel"]["B"]["mean"] == 128.0

    def test_multiple_pixels(self):
        pixels = [(100, 200, 50), (200, 100, 150), (0, 0, 0)]
        result = ppm_channel_stats(_doc(pixels))
        assert result["total_pixels"] == 3
        assert result["per_channel"]["R"]["min"] == 0
        assert result["per_channel"]["R"]["max"] == 200
        assert round(result["per_channel"]["R"]["mean"], 1) == round((100 + 200 + 0) / 3, 1)

    def test_black_image(self):
        pixels = [(0, 0, 0)] * 4
        result = ppm_channel_stats(_doc(pixels))
        assert result["per_channel"]["R"] == {"min": 0, "max": 0, "mean": 0.0}
        assert result["per_channel"]["G"] == {"min": 0, "max": 0, "mean": 0.0}

    def test_white_image(self):
        pixels = [(255, 255, 255)] * 4
        result = ppm_channel_stats(_doc(pixels))
        assert result["per_channel"]["B"]["max"] == 255
        assert result["per_channel"]["B"]["mean"] == 255.0

    def test_returns_correct_channels(self):
        result = ppm_channel_stats({"pixels": []})
        assert result["channels"] == ["R", "G", "B"]

    def test_partial_sample_note(self):
        # When pixel count < width*height, note should appear
        result = ppm_channel_stats(_doc([(1, 2, 3)], width=100, height=100))
        assert "note" in result  # partial sample note

    def test_callable_from_module(self):
        from src.python.ppm import ppm_stats
        assert callable(ppm_stats.ppm_channel_stats)
