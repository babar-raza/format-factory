"""
test_r155_pgm_histogram_threshold.py

Sprint: FORMAT-FACTORY-MAINSTREAM-PRODUCT-DEEPENING-RNEXT13-001
Added: 2026-06-09

Tests for PGM histogram and threshold functions.
Authority: P5 (SAL-PGM-00001, SAL-PGM-00002)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import histogram, threshold, write_pgm, parse_pgm_strict, PgmError


def _make_pgm(tmp_path: Path, width: int, height: int, maxval: int, pixels: list[int]) -> Path:
    p = tmp_path / "test.pgm"
    write_pgm(pixels, width, height, maxval, p)
    return p


class TestHistogram:
    """histogram: compute pixel value frequency distribution."""

    def test_basic_histogram(self, tmp_path):
        pixels = [0, 0, 128, 128, 128, 255]
        src = _make_pgm(tmp_path, 3, 2, 255, pixels)
        result = histogram(src)
        assert result["ok"] is True
        assert result["histogram"][0] == 2
        assert result["histogram"][128] == 3
        assert result["histogram"][255] == 1

    def test_unique_values_count(self, tmp_path):
        pixels = [10, 20, 30, 40]
        src = _make_pgm(tmp_path, 2, 2, 255, pixels)
        result = histogram(src)
        assert result["unique_values"] == 4

    def test_uniform_image(self, tmp_path):
        pixels = [100] * 9
        src = _make_pgm(tmp_path, 3, 3, 255, pixels)
        result = histogram(src)
        assert result["unique_values"] == 1
        assert result["histogram"][100] == 9

    def test_result_keys(self, tmp_path):
        src = _make_pgm(tmp_path, 1, 1, 255, [50])
        result = histogram(src)
        assert "ok" in result
        assert "width" in result
        assert "height" in result
        assert "maxval" in result
        assert "histogram" in result
        assert "unique_values" in result

    def test_nonexistent_raises(self, tmp_path):
        with pytest.raises(PgmError):
            histogram(tmp_path / "ghost.pgm")


class TestThreshold:
    """threshold: binary threshold a PGM image."""

    def test_threshold_basic(self, tmp_path):
        pixels = [0, 50, 100, 150, 200, 255]
        src = _make_pgm(tmp_path, 3, 2, 255, pixels)
        dst = tmp_path / "thresh.pgm"
        result = threshold(src, dst, value=128)
        assert result["ok"] is True
        assert result["above_count"] == 3  # 150, 200, 255
        assert result["below_count"] == 3  # 0, 50, 100

    def test_threshold_output_binary(self, tmp_path):
        pixels = [50, 200]
        src = _make_pgm(tmp_path, 2, 1, 255, pixels)
        dst = tmp_path / "binary.pgm"
        threshold(src, dst, value=100)
        img = parse_pgm_strict(dst)
        assert img.pixels == [0, 1]
        assert img.maxval == 1

    def test_threshold_all_above(self, tmp_path):
        pixels = [200, 250, 255]
        src = _make_pgm(tmp_path, 3, 1, 255, pixels)
        dst = tmp_path / "all_above.pgm"
        result = threshold(src, dst, value=100)
        assert result["above_count"] == 3
        assert result["below_count"] == 0

    def test_threshold_all_below(self, tmp_path):
        pixels = [0, 10, 20]
        src = _make_pgm(tmp_path, 3, 1, 255, pixels)
        dst = tmp_path / "all_below.pgm"
        result = threshold(src, dst, value=100)
        assert result["above_count"] == 0
        assert result["below_count"] == 3

    def test_threshold_preserves_dimensions(self, tmp_path):
        pixels = [i % 256 for i in range(12)]
        src = _make_pgm(tmp_path, 4, 3, 255, pixels)
        dst = tmp_path / "dims.pgm"
        threshold(src, dst, value=128)
        img = parse_pgm_strict(dst)
        assert img.width == 4
        assert img.height == 3

    def test_threshold_nonexistent_raises(self, tmp_path):
        with pytest.raises(PgmError):
            threshold(tmp_path / "ghost.pgm", tmp_path / "out.pgm", value=128)
