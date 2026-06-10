"""
test_r157_pbm_accessors.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT17-001
Added: 2026-06-10

Tests for PBM pixel_count and count_black functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import pixel_count, count_black, write_pbm, PbmError

_SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"


class TestPixelCount:
    def test_1x1(self):
        assert pixel_count(_SAMPLES / "1x1-black.pbm") == 1

    def test_2x2(self):
        assert pixel_count(_SAMPLES / "2x2-checker.pbm") == 4

    def test_3x2(self):
        assert pixel_count(_SAMPLES / "3x2-pattern.pbm") == 6

    def test_nonexistent_file(self):
        with pytest.raises(PbmError):
            pixel_count(_SAMPLES / "ghost.pbm")

    def test_written_file(self, tmp_path):
        p = tmp_path / "test.pbm"
        write_pbm([0, 1, 1, 0], 2, 2, p)
        assert pixel_count(p) == 4


class TestCountBlack:
    def test_1x1_black(self):
        assert count_black(_SAMPLES / "1x1-black.pbm") == 1

    def test_2x2_checker(self):
        count = count_black(_SAMPLES / "2x2-checker.pbm")
        assert count == 2

    def test_all_white(self, tmp_path):
        p = tmp_path / "white.pbm"
        write_pbm([0, 0, 0, 0], 2, 2, p)
        assert count_black(p) == 0

    def test_all_black(self, tmp_path):
        p = tmp_path / "black.pbm"
        write_pbm([1, 1, 1, 1, 1, 1], 3, 2, p)
        assert count_black(p) == 6

    def test_mixed(self, tmp_path):
        p = tmp_path / "mixed.pbm"
        write_pbm([1, 0, 1, 0, 1, 0], 3, 2, p)
        assert count_black(p) == 3

    def test_nonexistent_file(self):
        with pytest.raises(PbmError):
            count_black(_SAMPLES / "ghost.pbm")
