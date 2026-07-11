"""Tests for QOI image analytics extension functions."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_image_analytics import (
    qoi_width,
    qoi_height,
    qoi_colorspace,
    qoi_is_rgb,
    qoi_min_channel_value,
    qoi_max_channel_value,
)

SAMPLES = Path("samples/by-format/qoi/valid")
RED = SAMPLES / "1x1-red.qoi"
BLACK = SAMPLES / "2x2-black.qoi"
GRADIENT = SAMPLES / "4x1-gradient.qoi"
# 1x1-red.qoi: 1x1, 4 channels (RGBA), colorspace=0, pixels=[(255,0,0,255)]
# 2x2-black.qoi: 2x2, 4 channels (RGBA), colorspace=0, all pixels=(0,0,0,255)
# 4x1-gradient.qoi: 4x1, 3 channels (RGB), colorspace=0


# --- qoi_width ---

def test_width_red():
    assert qoi_width(RED) == 1


def test_width_black():
    assert qoi_width(BLACK) == 2


def test_width_gradient():
    assert qoi_width(GRADIENT) == 4


def test_width_returns_int():
    assert isinstance(qoi_width(RED), int)


# --- qoi_height ---

def test_height_red():
    assert qoi_height(RED) == 1


def test_height_black():
    assert qoi_height(BLACK) == 2


def test_height_gradient():
    assert qoi_height(GRADIENT) == 1


def test_height_returns_int():
    assert isinstance(qoi_height(RED), int)


# --- qoi_colorspace ---

def test_colorspace_red():
    assert qoi_colorspace(RED) == 0


def test_colorspace_gradient():
    assert qoi_colorspace(GRADIENT) == 0


def test_colorspace_returns_int():
    assert isinstance(qoi_colorspace(RED), int)


# --- qoi_is_rgb ---

def test_is_rgb_gradient():
    # 3-channel (RGB) => True
    assert qoi_is_rgb(GRADIENT) is True


def test_is_rgb_red():
    # 4-channel (RGBA) => False
    assert qoi_is_rgb(RED) is False


def test_is_rgb_black():
    # 4-channel (RGBA) => False
    assert qoi_is_rgb(BLACK) is False


def test_is_rgb_returns_bool():
    assert isinstance(qoi_is_rgb(RED), bool)


# --- qoi_min_channel_value ---

def test_min_channel_value_red():
    # (255, 0, 0, 255) => min=0
    assert qoi_min_channel_value(RED) == 0


def test_min_channel_value_black():
    # all (0,0,0,255) => min=0
    assert qoi_min_channel_value(BLACK) == 0


def test_min_channel_value_returns_int():
    assert isinstance(qoi_min_channel_value(RED), int)


# --- qoi_max_channel_value ---

def test_max_channel_value_red():
    # (255, 0, 0, 255) => max=255
    assert qoi_max_channel_value(RED) == 255


def test_max_channel_value_gradient():
    assert qoi_max_channel_value(GRADIENT) == 255


def test_max_channel_value_returns_int():
    assert isinstance(qoi_max_channel_value(RED), int)
