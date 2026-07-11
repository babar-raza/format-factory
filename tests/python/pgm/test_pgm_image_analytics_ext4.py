"""Tests for 6 new functions in pgm_image_analytics (ext4 batch)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pytest

from pgm.pgm_image_analytics import (
    pgm_is_standard_depth,
    pgm_is_high_depth,
    pgm_avg_pixel_value,
    pgm_is_portrait,
    pgm_is_ascii,
    pgm_is_all_white,
)

VALID = _REPO / "samples" / "by-format" / "pgm" / "valid"
WHITE = VALID / "1x1-white.pgm"       # P2 1x1 maxval=255 pixels=[255]
GRADIENT = VALID / "2x2-gradient.pgm" # P2 2x2 maxval=255 pixels=[0,85,170,255]
RAMP = VALID / "3x1-ramp.pgm"         # P2 3x1 maxval=255 pixels=[0,128,255]


# --- pgm_is_standard_depth ---

def test_is_standard_depth_white():
    assert pgm_is_standard_depth(WHITE) is True

def test_is_standard_depth_gradient():
    assert pgm_is_standard_depth(GRADIENT) is True

def test_is_standard_depth_ramp():
    assert pgm_is_standard_depth(RAMP) is True


# --- pgm_is_high_depth ---

def test_is_high_depth_white():
    # maxval=255 → not high depth
    assert pgm_is_high_depth(WHITE) is False

def test_is_high_depth_gradient():
    assert pgm_is_high_depth(GRADIENT) is False

def test_is_high_depth_ramp():
    assert pgm_is_high_depth(RAMP) is False


# --- pgm_avg_pixel_value ---

def test_avg_pixel_value_white():
    # single pixel of value 255
    assert pgm_avg_pixel_value(WHITE) == 255.0

def test_avg_pixel_value_gradient():
    # pixels=[0,85,170,255] → mean = 510/4 = 127.5
    assert pgm_avg_pixel_value(GRADIENT) == pytest.approx(127.5)

def test_avg_pixel_value_ramp():
    # pixels=[0,128,255] → mean = 383/3
    expected = (0 + 128 + 255) / 3
    assert pgm_avg_pixel_value(RAMP) == pytest.approx(expected)


# --- pgm_is_portrait ---

def test_is_portrait_white():
    # 1x1 — not portrait (equal)
    assert pgm_is_portrait(WHITE) is False

def test_is_portrait_gradient():
    # 2x2 — not portrait (equal)
    assert pgm_is_portrait(GRADIENT) is False

def test_is_portrait_ramp():
    # 3x1 — width=3, height=1 → landscape, not portrait
    assert pgm_is_portrait(RAMP) is False


# --- pgm_is_ascii ---

def test_is_ascii_white():
    # magic=P2 → ascii
    assert pgm_is_ascii(WHITE) is True

def test_is_ascii_gradient():
    assert pgm_is_ascii(GRADIENT) is True

def test_is_ascii_ramp():
    assert pgm_is_ascii(RAMP) is True


# --- pgm_is_all_white ---

def test_is_all_white_white():
    # single pixel = 255 = maxval → True
    assert pgm_is_all_white(WHITE) is True

def test_is_all_white_gradient():
    # pixels=[0,85,170,255] — not all 255 → False
    assert pgm_is_all_white(GRADIENT) is False

def test_is_all_white_ramp():
    # pixels=[0,128,255] — not all 255 → False
    assert pgm_is_all_white(RAMP) is False
