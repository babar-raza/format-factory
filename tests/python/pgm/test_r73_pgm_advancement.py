"""
test_r73_pgm_advancement.py — R73 Train G: PGM image_pixel_stats API.

Tests the new image_pixel_stats() function added in R73 Train G.
Verifies: min_value, max_value, mean_approx, total_pixels, return structure.

Sprint: FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.pgm.pgm_parser import image_pixel_stats

VALID = PROJECT_ROOT / "samples" / "by-format" / "pgm" / "valid"


def _write_p2(tmp_dir: Path, name: str, width: int, height: int,
              maxval: int, pixels: list[int]) -> Path:
    """Write a P2 PGM file to tmp_dir."""
    content = f"P2\n{width} {height}\n{maxval}\n" + " ".join(str(p) for p in pixels) + "\n"
    p = tmp_dir / name
    p.write_text(content, encoding="ascii")
    return p


class TestImagePixelStatsStructure:
    """R73-PGM-001: image_pixel_stats returns required fields."""

    def test_returns_ok_true_on_valid_file(self, tmp_path):
        f = _write_p2(tmp_path, "t.pgm", 2, 2, 255, [0, 128, 64, 255])
        result = image_pixel_stats(str(f))
        assert result["ok"] is True

    def test_returns_min_value(self, tmp_path):
        f = _write_p2(tmp_path, "t.pgm", 2, 2, 255, [10, 50, 100, 200])
        result = image_pixel_stats(str(f))
        assert result["min_value"] == 10

    def test_returns_max_value(self, tmp_path):
        f = _write_p2(tmp_path, "t.pgm", 2, 2, 255, [10, 50, 100, 200])
        result = image_pixel_stats(str(f))
        assert result["max_value"] == 200

    def test_mean_approx(self, tmp_path):
        # pixels: 0, 100, 200, 100 → mean = 100.0
        f = _write_p2(tmp_path, "t.pgm", 2, 2, 255, [0, 100, 200, 100])
        result = image_pixel_stats(str(f))
        assert abs(result["mean_approx"] - 100.0) < 0.01

    def test_total_pixels(self, tmp_path):
        f = _write_p2(tmp_path, "t.pgm", 3, 2, 255, [1, 2, 3, 4, 5, 6])
        result = image_pixel_stats(str(f))
        assert result["total_pixels"] == 6

    def test_uniform_image(self, tmp_path):
        f = _write_p2(tmp_path, "t.pgm", 2, 2, 255, [128, 128, 128, 128])
        result = image_pixel_stats(str(f))
        assert result["min_value"] == 128
        assert result["max_value"] == 128
        assert abs(result["mean_approx"] - 128.0) < 0.01

    def test_width_height_maxval_returned(self, tmp_path):
        f = _write_p2(tmp_path, "t.pgm", 4, 3, 15, [0] * 12)
        result = image_pixel_stats(str(f))
        assert result["width"] == 4
        assert result["height"] == 3
        assert result["maxval"] == 15

    def test_returns_ok_false_on_missing_file(self, tmp_path):
        result = image_pixel_stats(str(tmp_path / "nonexistent.pgm"))
        assert result["ok"] is False
        assert "error" in result

    def test_magic_field_present(self, tmp_path):
        f = _write_p2(tmp_path, "t.pgm", 1, 1, 255, [100])
        result = image_pixel_stats(str(f))
        assert result["magic"] == "P2"

    def test_corpus_valid_sample(self):
        """Sanity check against a committed corpus sample if present."""
        samples = list(VALID.glob("*.pgm")) if VALID.exists() else []
        if not samples:
            pytest.skip("No valid PGM corpus samples found")
        result = image_pixel_stats(str(samples[0]))
        assert result["ok"] is True
        assert result["min_value"] <= result["max_value"]
        assert result["total_pixels"] > 0
