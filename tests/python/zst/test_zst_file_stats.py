"""Tests for ZST file-level statistics module (zst_file_stats.py)."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst.zst_file_stats import (
    zst_is_well_compressed,
    zst_frames_are_equal_size,
    zst_is_tiny,
    zst_decompressed_per_frame,
    zst_is_size_reducing,
    zst_byte_overhead,
)

SAMPLES = Path("samples/by-format/zst/valid")
TEXT    = SAMPLES / "text-compressed.zst"    # comp=272, decomp=390, 1 frame, ratio=0.697
MINIMAL = SAMPLES / "minimal-synthetic.zst"  # comp=10,  decomp=1,   1 frame, ratio=10.0
RANDOM  = SAMPLES / "random-data.zst"        # comp=276, decomp=1024, 1 frame, ratio=0.269
BLOCK   = SAMPLES / "block-128k.zst"         # comp=131081, decomp=131068, 1 frame, ratio=1.000


# --- zst_is_well_compressed ---

def test_is_well_compressed_random():
    # random-data ratio=0.269 < 0.5
    assert zst_is_well_compressed(RANDOM) is True


def test_is_well_compressed_text():
    # text ratio=0.697 >= 0.5
    assert zst_is_well_compressed(TEXT) is False


def test_is_well_compressed_minimal():
    # minimal ratio=10.0 >= 0.5
    assert zst_is_well_compressed(MINIMAL) is False


def test_is_well_compressed_returns_bool():
    assert isinstance(zst_is_well_compressed(TEXT), bool)


# --- zst_frames_are_equal_size ---

def test_frames_equal_text():
    # single frame → min == max
    assert zst_frames_are_equal_size(TEXT) is True


def test_frames_equal_minimal():
    assert zst_frames_are_equal_size(MINIMAL) is True


def test_frames_equal_random():
    assert zst_frames_are_equal_size(RANDOM) is True


def test_frames_equal_returns_bool():
    assert isinstance(zst_frames_are_equal_size(TEXT), bool)


# --- zst_is_tiny ---

def test_is_tiny_minimal():
    # minimal comp=10 < 100
    assert zst_is_tiny(MINIMAL) is True


def test_is_tiny_text():
    # text comp=272 >= 100
    assert zst_is_tiny(TEXT) is False


def test_is_tiny_random():
    # random comp=276 >= 100
    assert zst_is_tiny(RANDOM) is False


def test_is_tiny_returns_bool():
    assert isinstance(zst_is_tiny(MINIMAL), bool)


# --- zst_decompressed_per_frame ---

def test_decompressed_per_frame_text():
    # text: 390 decomp / 1 frame = 390
    assert zst_decompressed_per_frame(TEXT) == 390


def test_decompressed_per_frame_random():
    # random: 1024 / 1 = 1024
    assert zst_decompressed_per_frame(RANDOM) == 1024


def test_decompressed_per_frame_minimal():
    # minimal: 1 / 1 = 1
    assert zst_decompressed_per_frame(MINIMAL) == 1


def test_decompressed_per_frame_returns_int():
    assert isinstance(zst_decompressed_per_frame(TEXT), int)


def test_decompressed_per_frame_positive():
    assert zst_decompressed_per_frame(TEXT) > 0


# --- zst_is_size_reducing ---

def test_is_size_reducing_text():
    # comp=272 < decomp=390 → True
    assert zst_is_size_reducing(TEXT) is True


def test_is_size_reducing_random():
    # comp=276 < decomp=1024 → True
    assert zst_is_size_reducing(RANDOM) is True


def test_is_size_reducing_minimal():
    # comp=10 > decomp=1 → False
    assert zst_is_size_reducing(MINIMAL) is False


def test_is_size_reducing_returns_bool():
    assert isinstance(zst_is_size_reducing(TEXT), bool)


# --- zst_byte_overhead ---

def test_byte_overhead_text():
    # 272 - 390 = -118
    assert zst_byte_overhead(TEXT) == -118


def test_byte_overhead_minimal():
    # 10 - 1 = 9
    assert zst_byte_overhead(MINIMAL) == 9


def test_byte_overhead_random():
    # 276 - 1024 = -748
    assert zst_byte_overhead(RANDOM) == -748


def test_byte_overhead_returns_int():
    assert isinstance(zst_byte_overhead(TEXT), int)
