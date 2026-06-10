"""
test_r158_pgm_accessors.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT18-001
Added: 2026-06-10

Tests for PGM pixel_count and average_gray functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import pixel_count, average_gray, write_pgm, PgmError

_SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"


class TestPixelCount:
    def test_1x1(self):
        assert pixel_count(_SAMPLES / "1x1-white.pgm") == 1

    def test_2x2(self):
        assert pixel_count(_SAMPLES / "2x2-gradient.pgm") == 4

    def test_3x1(self):
        assert pixel_count(_SAMPLES / "3x1-ramp.pgm") == 3

    def test_nonexistent_file(self):
        with pytest.raises(PgmError):
            pixel_count(_SAMPLES / "ghost.pgm")

    def test_written_file(self, tmp_path):
        p = tmp_path / "test.pgm"
        write_pgm([10, 20, 30, 40, 50, 60], 3, 2, 255, p)
        assert pixel_count(p) == 6


class TestAverageGray:
    def test_1x1_white(self):
        avg = average_gray(_SAMPLES / "1x1-white.pgm")
        assert avg == 255.0

    def test_uniform_value(self, tmp_path):
        p = tmp_path / "uniform.pgm"
        write_pgm([128, 128, 128, 128], 2, 2, 255, p)
        assert average_gray(p) == 128.0

    def test_gradient(self, tmp_path):
        p = tmp_path / "gradient.pgm"
        write_pgm([0, 100, 200], 3, 1, 255, p)
        assert average_gray(p) == 100.0

    def test_nonexistent_file(self):
        with pytest.raises(PgmError):
            average_gray(_SAMPLES / "ghost.pgm")

    def test_returns_float(self):
        avg = average_gray(_SAMPLES / "1x1-white.pgm")
        assert isinstance(avg, float)
