"""Tests for ppm_image_analytics extension (ext3 batch)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest
from src.python.ppm.ppm_image_analytics import (
    ppm_is_ascii,
    ppm_is_landscape,
    ppm_is_portrait,
    ppm_is_square,
    ppm_aspect_ratio,
    ppm_min_channel_value,
)

SAMPLES = Path("samples/by-format/ppm/valid")
RED_1X1 = SAMPLES / "1x1-red.ppm"
RGBW_2X2 = SAMPLES / "2x2-rgbw.ppm"
GRAD_3X1 = SAMPLES / "3x1-gradient.ppm"


# --- ppm_is_ascii ---

def test_is_ascii_returns_bool():
    assert isinstance(ppm_is_ascii(RED_1X1), bool)


def test_is_ascii_p3_true():
    assert ppm_is_ascii(RED_1X1) is True


def test_is_ascii_2x2_true():
    assert ppm_is_ascii(RGBW_2X2) is True


# --- ppm_is_landscape ---

def test_is_landscape_3x1_true():
    assert ppm_is_landscape(GRAD_3X1) is True


def test_is_landscape_1x1_false():
    assert ppm_is_landscape(RED_1X1) is False


def test_is_landscape_returns_bool():
    assert isinstance(ppm_is_landscape(RGBW_2X2), bool)


# --- ppm_is_portrait ---

def test_is_portrait_1x1_false():
    assert ppm_is_portrait(RED_1X1) is False


def test_is_portrait_3x1_false():
    # 3x1 is landscape (width=3, height=1), not portrait
    assert ppm_is_portrait(GRAD_3X1) is False


def test_is_portrait_returns_bool():
    assert isinstance(ppm_is_portrait(RED_1X1), bool)


# --- ppm_is_square ---

def test_is_square_1x1_true():
    assert ppm_is_square(RED_1X1) is True


def test_is_square_2x2_true():
    assert ppm_is_square(RGBW_2X2) is True


def test_is_square_3x1_false():
    assert ppm_is_square(GRAD_3X1) is False


# --- ppm_aspect_ratio ---

def test_aspect_ratio_1x1():
    assert ppm_aspect_ratio(RED_1X1) == pytest.approx(1.0)


def test_aspect_ratio_3x1():
    assert ppm_aspect_ratio(GRAD_3X1) == pytest.approx(3.0)


def test_aspect_ratio_returns_float():
    assert isinstance(ppm_aspect_ratio(RGBW_2X2), float)


# --- ppm_min_channel_value ---

def test_min_channel_value_returns_int():
    assert isinstance(ppm_min_channel_value(RED_1X1), int)


def test_min_channel_value_nonneg():
    assert ppm_min_channel_value(RED_1X1) >= 0
