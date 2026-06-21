"""
Sprint 47 — 5 new QOI analytics functions.
Tests: qoi_file_size_bytes, qoi_avg_red_channel, qoi_avg_green_channel,
       qoi_red_dominant_count, qoi_col_uniformity
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import (
    qoi_file_size_bytes,
    qoi_avg_red_channel,
    qoi_avg_green_channel,
    qoi_red_dominant_count,
    qoi_col_uniformity,
)

_SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_SAMPLES / "1x1-red.qoi")
_BLACK = str(_SAMPLES / "2x2-black.qoi")
_GRADIENT = str(_SAMPLES / "4x1-gradient.qoi")


# --- qoi_file_size_bytes ---

def test_file_size_bytes_red_is_int():
    assert isinstance(qoi_file_size_bytes(_RED), int)


def test_file_size_bytes_red_positive():
    assert qoi_file_size_bytes(_RED) > 0


def test_file_size_bytes_black_positive():
    assert qoi_file_size_bytes(_BLACK) > 0


def test_file_size_bytes_consistent_with_stat():
    import os
    assert qoi_file_size_bytes(_RED) == os.path.getsize(_RED)


# --- qoi_avg_red_channel ---

def test_avg_red_channel_red_is_float():
    assert isinstance(qoi_avg_red_channel(_RED), float)


def test_avg_red_channel_red_nonneg():
    assert qoi_avg_red_channel(_RED) >= 0.0


def test_avg_red_channel_black_nonneg():
    assert qoi_avg_red_channel(_BLACK) >= 0.0


def test_avg_red_channel_gradient_nonneg():
    assert qoi_avg_red_channel(_GRADIENT) >= 0.0


# --- qoi_avg_green_channel ---

def test_avg_green_channel_red_is_float():
    assert isinstance(qoi_avg_green_channel(_RED), float)


def test_avg_green_channel_red_nonneg():
    assert qoi_avg_green_channel(_RED) >= 0.0


def test_avg_green_channel_black_nonneg():
    assert qoi_avg_green_channel(_BLACK) >= 0.0


def test_avg_green_channel_gradient_nonneg():
    assert qoi_avg_green_channel(_GRADIENT) >= 0.0


# --- qoi_red_dominant_count ---

def test_red_dominant_count_red_is_int():
    assert isinstance(qoi_red_dominant_count(_RED), int)


def test_red_dominant_count_red_nonneg():
    assert qoi_red_dominant_count(_RED) >= 0


def test_red_dominant_count_black_nonneg():
    assert qoi_red_dominant_count(_BLACK) >= 0


def test_red_dominant_count_gradient_nonneg():
    assert qoi_red_dominant_count(_GRADIENT) >= 0


# --- qoi_col_uniformity ---

def test_col_uniformity_red_is_float():
    assert isinstance(qoi_col_uniformity(_RED), float)


def test_col_uniformity_red_is_one():
    # 1x1 — single column is uniform
    assert qoi_col_uniformity(_RED) == 1.0


def test_col_uniformity_black_between_zero_and_one():
    result = qoi_col_uniformity(_BLACK)
    assert 0.0 <= result <= 1.0


def test_col_uniformity_gradient_nonneg():
    assert qoi_col_uniformity(_GRADIENT) >= 0.0
