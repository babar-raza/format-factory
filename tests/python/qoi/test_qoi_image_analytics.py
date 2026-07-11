"""Tests for QOI image analytics module."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_image_analytics import (
    qoi_is_landscape,
    qoi_is_portrait,
    qoi_is_square,
    qoi_has_alpha,
    qoi_total_pixels,
    qoi_is_monochrome,
)

SAMPLES = Path("samples/by-format/qoi/valid")
RED = SAMPLES / "1x1-red.qoi"        # 1x1, 4 channels, red pixel (not monochrome)
BLACK = SAMPLES / "2x2-black.qoi"    # 2x2, 4 channels, all black (monochrome)
GRADIENT = SAMPLES / "4x1-gradient.qoi"  # 4x1, 3 channels, landscape


# --- qoi_is_landscape ---

def test_is_landscape_gradient():
    assert qoi_is_landscape(GRADIENT) is True  # 4x1 -> width > height


def test_is_landscape_square():
    assert qoi_is_landscape(RED) is False  # 1x1 not landscape


def test_is_landscape_returns_bool():
    assert isinstance(qoi_is_landscape(GRADIENT), bool)


# --- qoi_is_portrait ---

def test_is_portrait_gradient():
    assert qoi_is_portrait(GRADIENT) is False  # 4x1 not portrait


def test_is_portrait_square():
    assert qoi_is_portrait(RED) is False  # 1x1 not portrait


def test_is_portrait_returns_bool():
    assert isinstance(qoi_is_portrait(RED), bool)


# --- qoi_is_square ---

def test_is_square_red():
    assert qoi_is_square(RED) is True  # 1x1


def test_is_square_black():
    assert qoi_is_square(BLACK) is True  # 2x2


def test_is_square_gradient():
    assert qoi_is_square(GRADIENT) is False  # 4x1


def test_is_square_returns_bool():
    assert isinstance(qoi_is_square(RED), bool)


# --- qoi_has_alpha ---

def test_has_alpha_red():
    assert qoi_has_alpha(RED) is True  # 4 channels


def test_has_alpha_black():
    assert qoi_has_alpha(BLACK) is True  # 4 channels


def test_has_alpha_gradient():
    assert qoi_has_alpha(GRADIENT) is False  # 3 channels (RGB only)


def test_has_alpha_returns_bool():
    assert isinstance(qoi_has_alpha(RED), bool)


# --- qoi_total_pixels ---

def test_total_pixels_red():
    assert qoi_total_pixels(RED) == 1  # 1x1


def test_total_pixels_black():
    assert qoi_total_pixels(BLACK) == 4  # 2x2


def test_total_pixels_gradient():
    assert qoi_total_pixels(GRADIENT) == 4  # 4x1


def test_total_pixels_returns_int():
    assert isinstance(qoi_total_pixels(RED), int)


# --- qoi_is_monochrome ---

def test_is_monochrome_black():
    assert qoi_is_monochrome(BLACK) is True  # all (0,0,0,255)


def test_is_monochrome_red():
    assert qoi_is_monochrome(RED) is False  # (255,0,0,255) — R≠G


def test_is_monochrome_returns_bool():
    assert isinstance(qoi_is_monochrome(BLACK), bool)
