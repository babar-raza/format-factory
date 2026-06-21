"""
Sprint 103 — ZST analytics round 4.
25 tests for 5 new analytics functions:
  zst_decompressed_byte_sum, zst_compressed_to_decompressed_diff,
  zst_frame_count_exceeds_one, zst_max_byte_value, zst_min_byte_value
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_decompressed_byte_sum,
    zst_compressed_to_decompressed_diff,
    zst_frame_count_exceeds_one,
    zst_max_byte_value,
    zst_min_byte_value,
)

_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-synthetic.zst")
_RANDOM = str(_SAMPLES / "random-data.zst")
_TEXT = str(_SAMPLES / "text-compressed.zst")


# --- zst_decompressed_byte_sum ---

class TestZstDecompressedByteSum:
    def test_returns_int(self):
        result = zst_decompressed_byte_sum(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_decompressed_byte_sum(_MINIMAL)
        assert result >= 0

    def test_random_positive(self):
        result = zst_decompressed_byte_sum(_RANDOM)
        assert result > 0

    def test_text_positive(self):
        result = zst_decompressed_byte_sum(_TEXT)
        assert result > 0

    def test_is_int_not_float(self):
        result = zst_decompressed_byte_sum(_RANDOM)
        assert type(result) is int


# --- zst_compressed_to_decompressed_diff ---

class TestZstCompressedToDecompressedDiff:
    def test_returns_int(self):
        result = zst_compressed_to_decompressed_diff(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_to_decompressed_diff(_MINIMAL)
        assert result >= 0

    def test_random_non_negative(self):
        result = zst_compressed_to_decompressed_diff(_RANDOM)
        assert result >= 0

    def test_text_non_negative(self):
        result = zst_compressed_to_decompressed_diff(_TEXT)
        assert result >= 0

    def test_is_absolute(self):
        # Verify result is non-negative regardless of which is larger
        result = zst_compressed_to_decompressed_diff(_MINIMAL)
        assert result == abs(result)


# --- zst_frame_count_exceeds_one ---

class TestZstFrameCountExceedsOne:
    def test_returns_bool(self):
        result = zst_frame_count_exceeds_one(_MINIMAL)
        assert isinstance(result, bool)

    def test_minimal_single_frame(self):
        # minimal-synthetic is a single frame
        result = zst_frame_count_exceeds_one(_MINIMAL)
        assert result is False

    def test_random_bool(self):
        result = zst_frame_count_exceeds_one(_RANDOM)
        assert isinstance(result, bool)

    def test_text_bool(self):
        result = zst_frame_count_exceeds_one(_TEXT)
        assert isinstance(result, bool)

    def test_consistent_with_frame_count(self):
        from src.python.zst import zst_frame_count
        fc = zst_frame_count(_MINIMAL)
        expected = fc > 1
        assert zst_frame_count_exceeds_one(_MINIMAL) == expected


# --- zst_max_byte_value ---

class TestZstMaxByteValue:
    def test_returns_int(self):
        result = zst_max_byte_value(_MINIMAL)
        assert isinstance(result, int)

    def test_bounded_0_to_255(self):
        result = zst_max_byte_value(_MINIMAL)
        assert 0 <= result <= 255

    def test_random_positive(self):
        result = zst_max_byte_value(_RANDOM)
        assert result > 0

    def test_text_positive(self):
        result = zst_max_byte_value(_TEXT)
        assert result > 0

    def test_gte_min_byte_value(self):
        mx = zst_max_byte_value(_RANDOM)
        mn = zst_min_byte_value(_RANDOM)
        assert mx >= mn


# --- zst_min_byte_value ---

class TestZstMinByteValue:
    def test_returns_int(self):
        result = zst_min_byte_value(_MINIMAL)
        assert isinstance(result, int)

    def test_bounded_0_to_255(self):
        result = zst_min_byte_value(_MINIMAL)
        assert 0 <= result <= 255

    def test_random_bounded(self):
        result = zst_min_byte_value(_RANDOM)
        assert 0 <= result <= 255

    def test_text_bounded(self):
        result = zst_min_byte_value(_TEXT)
        assert 0 <= result <= 255

    def test_lte_max_byte_value(self):
        mn = zst_min_byte_value(_RANDOM)
        mx = zst_max_byte_value(_RANDOM)
        assert mn <= mx
