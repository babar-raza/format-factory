"""
test_r73_pbm_advancement.py — R73 Train G: PBM image_pixel_stats API.

Tests the new image_pixel_stats() function added in R73 Train G.
Verifies: black_count, white_count, black_density, total_pixels, return structure.

Sprint: FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.pbm.pbm_parser import image_pixel_stats, parse_pbm_strict

VALID = PROJECT_ROOT / "samples" / "by-format" / "pbm" / "valid"


def _write_p1(tmp_dir: Path, name: str, width: int, height: int, pixels: list[int]) -> Path:
    """Write a P1 PBM file to tmp_dir."""
    content = f"P1\n{width} {height}\n" + " ".join(str(p) for p in pixels) + "\n"
    p = tmp_dir / name
    p.write_text(content, encoding="ascii")
    return p


class TestImagePixelStatsStructure:
    """R73-PBM-001: image_pixel_stats returns required fields."""

    def test_returns_ok_true_on_valid_file(self, tmp_path):
        f = _write_p1(tmp_path, "t.pbm", 2, 2, [0, 1, 1, 0])
        result = image_pixel_stats(str(f))
        assert result["ok"] is True

    def test_returns_black_count(self, tmp_path):
        f = _write_p1(tmp_path, "t.pbm", 2, 2, [0, 1, 1, 0])
        result = image_pixel_stats(str(f))
        assert result["black_count"] == 2

    def test_returns_white_count(self, tmp_path):
        f = _write_p1(tmp_path, "t.pbm", 2, 2, [0, 1, 1, 0])
        result = image_pixel_stats(str(f))
        assert result["white_count"] == 2

    def test_black_density_half(self, tmp_path):
        f = _write_p1(tmp_path, "t.pbm", 2, 2, [0, 1, 1, 0])
        result = image_pixel_stats(str(f))
        assert abs(result["black_density"] - 0.5) < 0.0001

    def test_total_pixels(self, tmp_path):
        f = _write_p1(tmp_path, "t.pbm", 3, 1, [1, 0, 1])
        result = image_pixel_stats(str(f))
        assert result["total_pixels"] == 3

    def test_all_black(self, tmp_path):
        f = _write_p1(tmp_path, "t.pbm", 2, 2, [1, 1, 1, 1])
        result = image_pixel_stats(str(f))
        assert result["black_count"] == 4
        assert result["white_count"] == 0
        assert abs(result["black_density"] - 1.0) < 0.0001

    def test_all_white(self, tmp_path):
        f = _write_p1(tmp_path, "t.pbm", 2, 2, [0, 0, 0, 0])
        result = image_pixel_stats(str(f))
        assert result["black_count"] == 0
        assert result["white_count"] == 4
        assert abs(result["black_density"] - 0.0) < 0.0001

    def test_width_height_returned(self, tmp_path):
        f = _write_p1(tmp_path, "t.pbm", 4, 3, [0] * 12)
        result = image_pixel_stats(str(f))
        assert result["width"] == 4
        assert result["height"] == 3

    def test_returns_ok_false_on_missing_file(self, tmp_path):
        result = image_pixel_stats(str(tmp_path / "nonexistent.pbm"))
        assert result["ok"] is False
        assert "error" in result

    def test_corpus_valid_sample(self):
        """Sanity check against a committed corpus sample if present."""
        samples = list(VALID.glob("*.pbm")) if VALID.exists() else []
        if not samples:
            pytest.skip("No valid PBM corpus samples found")
        result = image_pixel_stats(str(samples[0]))
        assert result["ok"] is True
        assert result["total_pixels"] == result["black_count"] + result["white_count"]
