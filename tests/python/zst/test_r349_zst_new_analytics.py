"""
Sprint 85 — ZST analytics round 3.
25 tests for 5 new analytics functions:
  zst_content_entropy, zst_avg_byte_value, zst_size_per_frame,
  zst_byte_ratio, zst_compression_savings_ratio
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_content_entropy,
    zst_avg_byte_value,
    zst_size_per_frame,
    zst_byte_ratio,
    zst_compression_savings_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"
_RANDOM = str(_SAMPLES / "random-data.zst")
_MINIMAL = str(_SAMPLES / "minimal-synthetic.zst")
_BLOCK = str(_SAMPLES / "block-128k.zst")


# --- zst_content_entropy ---

class TestZstContentEntropy:
    def test_returns_float(self):
        result = zst_content_entropy(_RANDOM)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = zst_content_entropy(_RANDOM)
        assert result >= 0.0

    def test_random_data_high_entropy(self):
        result = zst_content_entropy(_RANDOM)
        assert result > 0.0

    def test_bounded_by_8(self):
        result = zst_content_entropy(_RANDOM)
        assert result <= 8.0

    def test_block_file(self):
        result = zst_content_entropy(_BLOCK)
        assert isinstance(result, float) and result >= 0.0


# --- zst_avg_byte_value ---

class TestZstAvgByteValue:
    def test_returns_float(self):
        result = zst_avg_byte_value(_RANDOM)
        assert isinstance(result, float)

    def test_bounded_0_to_255(self):
        result = zst_avg_byte_value(_RANDOM)
        assert 0.0 <= result <= 255.0

    def test_random_data_near_127(self):
        result = zst_avg_byte_value(_RANDOM)
        assert 100.0 <= result <= 155.0

    def test_block_file(self):
        result = zst_avg_byte_value(_BLOCK)
        assert isinstance(result, float) and result >= 0.0

    def test_minimal_returns_float(self):
        result = zst_avg_byte_value(_MINIMAL)
        assert isinstance(result, float)


# --- zst_size_per_frame ---

class TestZstSizePerFrame:
    def test_returns_float(self):
        result = zst_size_per_frame(_RANDOM)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = zst_size_per_frame(_RANDOM)
        assert result >= 0.0

    def test_minimal_file(self):
        result = zst_size_per_frame(_MINIMAL)
        assert result >= 0.0

    def test_block_file(self):
        result = zst_size_per_frame(_BLOCK)
        assert isinstance(result, float) and result >= 0.0

    def test_positive_for_valid_file(self):
        result = zst_size_per_frame(_RANDOM)
        assert result > 0.0


# --- zst_byte_ratio ---

class TestZstByteRatio:
    def test_returns_float(self):
        result = zst_byte_ratio(_RANDOM)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = zst_byte_ratio(_RANDOM)
        assert result >= 0.0

    def test_random_data_decompresses(self):
        result = zst_byte_ratio(_RANDOM)
        assert result > 0.0

    def test_block_file(self):
        result = zst_byte_ratio(_BLOCK)
        assert isinstance(result, float) and result >= 0.0

    def test_minimal_file(self):
        result = zst_byte_ratio(_MINIMAL)
        assert isinstance(result, float)


# --- zst_compression_savings_ratio ---

class TestZstCompressionSavingsRatio:
    def test_returns_float(self):
        result = zst_compression_savings_ratio(_RANDOM)
        assert isinstance(result, float)

    def test_random_data_savings_positive(self):
        result = zst_compression_savings_ratio(_RANDOM)
        assert result > 0.0

    def test_minimal_file(self):
        result = zst_compression_savings_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_block_file(self):
        result = zst_compression_savings_ratio(_BLOCK)
        assert isinstance(result, float)

    def test_bounded_below_1(self):
        result = zst_compression_savings_ratio(_RANDOM)
        assert result < 1.0
