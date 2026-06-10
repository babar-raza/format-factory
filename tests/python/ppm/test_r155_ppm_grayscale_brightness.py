"""
test_r155_ppm_grayscale_brightness.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT13-001
Added: 2026-06-09

Tests for PPM to_grayscale and brightness functions.
Authority: P5 (FACT-PPM-001, FACT-PPM-002)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import to_grayscale, brightness, write_ppm, parse_ppm_strict, PpmError


def _make_ppm(tmp_path: Path, width: int, height: int, maxval: int,
              pixels: list[tuple[int, int, int]]) -> Path:
    p = tmp_path / "test.ppm"
    write_ppm(pixels, width, height, maxval, p)
    return p


class TestToGrayscale:
    """to_grayscale: convert PPM color to PGM grayscale."""

    def test_pure_white(self, tmp_path):
        src = _make_ppm(tmp_path, 1, 1, 255, [(255, 255, 255)])
        dst = tmp_path / "gray.pgm"
        result = to_grayscale(src, dst)
        assert result["ok"] is True
        content = dst.read_text()
        assert content.startswith("P2")

    def test_pure_black(self, tmp_path):
        src = _make_ppm(tmp_path, 1, 1, 255, [(0, 0, 0)])
        dst = tmp_path / "gray.pgm"
        to_grayscale(src, dst)
        # Parse manually: should have pixel value 0
        lines = dst.read_text().strip().split("\n")
        assert lines[-1].strip() == "0"

    def test_red_channel(self, tmp_path):
        src = _make_ppm(tmp_path, 1, 1, 255, [(255, 0, 0)])
        dst = tmp_path / "gray.pgm"
        to_grayscale(src, dst)
        lines = dst.read_text().strip().split("\n")
        gray_val = int(lines[-1].strip())
        # 0.299 * 255 ≈ 76
        assert 75 <= gray_val <= 77

    def test_preserves_dimensions(self, tmp_path):
        pixels = [(100, 100, 100)] * 6
        src = _make_ppm(tmp_path, 3, 2, 255, pixels)
        dst = tmp_path / "gray.pgm"
        result = to_grayscale(src, dst)
        assert result["width"] == 3
        assert result["height"] == 2

    def test_result_keys(self, tmp_path):
        src = _make_ppm(tmp_path, 1, 1, 255, [(128, 128, 128)])
        dst = tmp_path / "gray.pgm"
        result = to_grayscale(src, dst)
        assert "ok" in result
        assert "width" in result
        assert "maxval" in result
        assert "pixel_count" in result

    def test_nonexistent_raises(self, tmp_path):
        with pytest.raises(PpmError):
            to_grayscale(tmp_path / "ghost.ppm", tmp_path / "out.pgm")


class TestBrightness:
    """brightness: adjust PPM brightness by delta."""

    def test_positive_delta(self, tmp_path):
        pixels = [(100, 100, 100)]
        src = _make_ppm(tmp_path, 1, 1, 255, pixels)
        dst = tmp_path / "bright.ppm"
        result = brightness(src, dst, delta=50)
        assert result["ok"] is True
        img = parse_ppm_strict(dst)
        assert img.pixels[0] == (150, 150, 150)

    def test_negative_delta(self, tmp_path):
        pixels = [(100, 100, 100)]
        src = _make_ppm(tmp_path, 1, 1, 255, pixels)
        dst = tmp_path / "dark.ppm"
        brightness(src, dst, delta=-50)
        img = parse_ppm_strict(dst)
        assert img.pixels[0] == (50, 50, 50)

    def test_clamping_high(self, tmp_path):
        pixels = [(200, 200, 200)]
        src = _make_ppm(tmp_path, 1, 1, 255, pixels)
        dst = tmp_path / "clamp_hi.ppm"
        result = brightness(src, dst, delta=100)
        img = parse_ppm_strict(dst)
        assert img.pixels[0] == (255, 255, 255)
        assert result["clamped_count"] == 1

    def test_clamping_low(self, tmp_path):
        pixels = [(20, 20, 20)]
        src = _make_ppm(tmp_path, 1, 1, 255, pixels)
        dst = tmp_path / "clamp_lo.ppm"
        result = brightness(src, dst, delta=-50)
        img = parse_ppm_strict(dst)
        assert img.pixels[0] == (0, 0, 0)
        assert result["clamped_count"] == 1

    def test_zero_delta_preserves(self, tmp_path):
        pixels = [(100, 150, 200)]
        src = _make_ppm(tmp_path, 1, 1, 255, pixels)
        dst = tmp_path / "same.ppm"
        brightness(src, dst, delta=0)
        img = parse_ppm_strict(dst)
        assert img.pixels[0] == (100, 150, 200)

    def test_preserves_dimensions(self, tmp_path):
        pixels = [(50, 50, 50)] * 6
        src = _make_ppm(tmp_path, 3, 2, 255, pixels)
        dst = tmp_path / "br.ppm"
        result = brightness(src, dst, delta=10)
        assert result["width"] == 3
        assert result["height"] == 2

    def test_nonexistent_raises(self, tmp_path):
        with pytest.raises(PpmError):
            brightness(tmp_path / "ghost.ppm", tmp_path / "out.ppm", delta=10)
