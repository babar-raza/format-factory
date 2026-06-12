"""Tests for pbm_to_pgm.pbm_pixels_to_pgm_pixels() — Sprint 4 Lane D (LFI-6-D).

Verifies PBM pixel list conversion to PGM pixel list.
PBM: 0=white, 1=black
PGM: 0=black, maxval=white
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels


def test_empty_pixels_returns_empty():
    assert pbm_pixels_to_pgm_pixels([]) == []


def test_black_pixel_converts_to_zero():
    # PBM black=1 → PGM black=0
    result = pbm_pixels_to_pgm_pixels([1])
    assert result == [0]


def test_white_pixel_converts_to_maxval():
    # PBM white=0 → PGM white=maxval (default 255)
    result = pbm_pixels_to_pgm_pixels([0])
    assert result == [255]


def test_default_maxval_is_255():
    result = pbm_pixels_to_pgm_pixels([0, 1])
    assert result == [255, 0]


def test_custom_maxval():
    result = pbm_pixels_to_pgm_pixels([0, 1], maxval=100)
    assert result == [100, 0]


def test_multiple_pixels_converted():
    pbm = [0, 1, 0, 1, 1]
    result = pbm_pixels_to_pgm_pixels(pbm, maxval=255)
    assert result == [255, 0, 255, 0, 0]


def test_returns_list():
    result = pbm_pixels_to_pgm_pixels([0, 1])
    assert isinstance(result, list)


def test_maxval_1_converts_correctly():
    result = pbm_pixels_to_pgm_pixels([0, 1], maxval=1)
    assert result == [1, 0]


def test_invalid_maxval_zero_raises():
    with pytest.raises(ValueError):
        pbm_pixels_to_pgm_pixels([0], maxval=0)


def test_invalid_maxval_256_raises():
    with pytest.raises(ValueError):
        pbm_pixels_to_pgm_pixels([0], maxval=256)
