"""
test_r159_pgm_threshold_minmax.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT19-001
Added: 2026-06-10

Tests for PGM count_above_threshold and min_max_gray functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import count_above_threshold, min_max_gray, write_pgm, PgmError

_SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"


class TestCountAboveThreshold:
    def test_all_above(self, tmp_path):
        p = tmp_path / "test.pgm"
        write_pgm([200, 200, 200, 200], 2, 2, 255, p)
        assert count_above_threshold(p, 100) == 4

    def test_none_above(self, tmp_path):
        p = tmp_path / "test.pgm"
        write_pgm([50, 50, 50, 50], 2, 2, 255, p)
        assert count_above_threshold(p, 100) == 0

    def test_mixed(self, tmp_path):
        p = tmp_path / "test.pgm"
        write_pgm([50, 150, 50, 200], 2, 2, 255, p)
        assert count_above_threshold(p, 100) == 2

    def test_boundary(self, tmp_path):
        p = tmp_path / "test.pgm"
        write_pgm([100, 101], 2, 1, 255, p)
        assert count_above_threshold(p, 100) == 1

    def test_nonexistent_file(self):
        with pytest.raises(PgmError):
            count_above_threshold(_SAMPLES / "ghost.pgm", 100)


class TestMinMaxGray:
    def test_uniform(self, tmp_path):
        p = tmp_path / "test.pgm"
        write_pgm([128, 128, 128], 3, 1, 255, p)
        assert min_max_gray(p) == (128, 128)

    def test_range(self, tmp_path):
        p = tmp_path / "test.pgm"
        write_pgm([10, 200, 50, 150], 2, 2, 255, p)
        assert min_max_gray(p) == (10, 200)

    def test_single_pixel(self, tmp_path):
        p = tmp_path / "test.pgm"
        write_pgm([42], 1, 1, 255, p)
        assert min_max_gray(p) == (42, 42)

    def test_1x1_white_sample(self):
        assert min_max_gray(_SAMPLES / "1x1-white.pgm") == (255, 255)

    def test_nonexistent_file(self):
        with pytest.raises(PgmError):
            min_max_gray(_SAMPLES / "ghost.pgm")
