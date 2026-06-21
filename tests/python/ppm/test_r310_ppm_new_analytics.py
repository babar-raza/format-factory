"""
Sprint 46 — 5 new PPM analytics functions.
Tests: ppm_file_size_bytes, ppm_unique_pixel_count, ppm_red_dominant_count,
       ppm_avg_red_channel, ppm_col_uniformity
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import (
    ppm_file_size_bytes,
    ppm_unique_pixel_count,
    ppm_red_dominant_count,
    ppm_avg_red_channel,
    ppm_col_uniformity,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_SAMPLES / "1x1-red.ppm")
_RGBW = str(_SAMPLES / "2x2-rgbw.ppm")
_GRADIENT = str(_SAMPLES / "3x1-gradient.ppm")


# --- ppm_file_size_bytes ---

def test_file_size_bytes_red_is_int():
    assert isinstance(ppm_file_size_bytes(_RED), int)


def test_file_size_bytes_red_positive():
    assert ppm_file_size_bytes(_RED) > 0


def test_file_size_bytes_rgbw_positive():
    assert ppm_file_size_bytes(_RGBW) > 0


def test_file_size_bytes_consistent_with_stat():
    import os
    assert ppm_file_size_bytes(_RED) == os.path.getsize(_RED)


# --- ppm_unique_pixel_count ---

def test_unique_pixel_count_red_is_int():
    assert isinstance(ppm_unique_pixel_count(_RED), int)


def test_unique_pixel_count_red_positive():
    assert ppm_unique_pixel_count(_RED) >= 1


def test_unique_pixel_count_rgbw_positive():
    assert ppm_unique_pixel_count(_RGBW) >= 1


def test_unique_pixel_count_gradient_positive():
    assert ppm_unique_pixel_count(_GRADIENT) >= 1


# --- ppm_red_dominant_count ---

def test_red_dominant_count_red_is_int():
    assert isinstance(ppm_red_dominant_count(_RED), int)


def test_red_dominant_count_red_positive():
    # 1x1 pure red — red dominates
    assert ppm_red_dominant_count(_RED) >= 1


def test_red_dominant_count_rgbw_nonneg():
    assert ppm_red_dominant_count(_RGBW) >= 0


def test_red_dominant_count_gradient_nonneg():
    assert ppm_red_dominant_count(_GRADIENT) >= 0


# --- ppm_avg_red_channel ---

def test_avg_red_channel_red_is_float():
    assert isinstance(ppm_avg_red_channel(_RED), float)


def test_avg_red_channel_red_nonneg():
    assert ppm_avg_red_channel(_RED) >= 0.0


def test_avg_red_channel_rgbw_nonneg():
    assert ppm_avg_red_channel(_RGBW) >= 0.0


def test_avg_red_channel_gradient_nonneg():
    assert ppm_avg_red_channel(_GRADIENT) >= 0.0


# --- ppm_col_uniformity ---

def test_col_uniformity_red_is_float():
    assert isinstance(ppm_col_uniformity(_RED), float)


def test_col_uniformity_red_is_one():
    # 1x1 — single column is always uniform
    assert ppm_col_uniformity(_RED) == 1.0


def test_col_uniformity_rgbw_between_zero_and_one():
    result = ppm_col_uniformity(_RGBW)
    assert 0.0 <= result <= 1.0


def test_col_uniformity_gradient_nonneg():
    assert ppm_col_uniformity(_GRADIENT) >= 0.0
