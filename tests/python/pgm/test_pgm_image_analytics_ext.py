"""Tests for pgm_image_analytics extension functions."""
from __future__ import annotations

from pathlib import Path

import pytest

from pgm.pgm_image_analytics import (
    pgm_total_pixels,
    pgm_is_square,
    pgm_is_landscape,
    pgm_aspect_ratio,
    pgm_min_pixel_value,
    pgm_max_pixel_value,
)

SAMPLES = Path("samples/by-format/pgm/valid")
ONEX1 = SAMPLES / "1x1-white.pgm"
TWOX2 = SAMPLES / "2x2-gradient.pgm"
THREEX1 = SAMPLES / "3x1-ramp.pgm"


# --- pgm_total_pixels ---

def test_total_pixels_1x1():
    assert pgm_total_pixels(ONEX1) == 1


def test_total_pixels_2x2():
    assert pgm_total_pixels(TWOX2) == 4


def test_total_pixels_3x1():
    assert pgm_total_pixels(THREEX1) == 3


def test_total_pixels_returns_int():
    assert isinstance(pgm_total_pixels(ONEX1), int)


# --- pgm_is_square ---

def test_is_square_1x1():
    assert pgm_is_square(ONEX1) is True


def test_is_square_2x2():
    assert pgm_is_square(TWOX2) is True


def test_is_square_3x1_false():
    assert pgm_is_square(THREEX1) is False


def test_is_square_returns_bool():
    assert isinstance(pgm_is_square(ONEX1), bool)


# --- pgm_is_landscape ---

def test_is_landscape_3x1():
    assert pgm_is_landscape(THREEX1) is True


def test_is_landscape_1x1_false():
    assert pgm_is_landscape(ONEX1) is False


def test_is_landscape_returns_bool():
    assert isinstance(pgm_is_landscape(TWOX2), bool)


# --- pgm_aspect_ratio ---

def test_aspect_ratio_1x1():
    assert pgm_aspect_ratio(ONEX1) == pytest.approx(1.0)


def test_aspect_ratio_3x1():
    assert pgm_aspect_ratio(THREEX1) == pytest.approx(3.0)


def test_aspect_ratio_returns_float():
    assert isinstance(pgm_aspect_ratio(TWOX2), float)


# --- pgm_min_pixel_value ---

def test_min_pixel_value_1x1_white():
    # 1x1 white = 255
    assert pgm_min_pixel_value(ONEX1) == 255


def test_min_pixel_value_2x2_gradient():
    # gradient has min 0
    assert pgm_min_pixel_value(TWOX2) == 0


def test_min_pixel_value_returns_int():
    assert isinstance(pgm_min_pixel_value(ONEX1), int)


# --- pgm_max_pixel_value ---

def test_max_pixel_value_1x1_white():
    assert pgm_max_pixel_value(ONEX1) == 255


def test_max_pixel_value_2x2_gradient():
    assert pgm_max_pixel_value(TWOX2) == 255


def test_max_pixel_value_returns_int():
    assert isinstance(pgm_max_pixel_value(TWOX2), int)
