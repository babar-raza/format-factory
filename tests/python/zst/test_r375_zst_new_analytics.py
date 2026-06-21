"""
Sprint ff-idempotent-spec-to-feature-swarm-20260617 — ZST analytics deepening.
Tests for two new analytics functions:
  zst_file_size_bytes_times_eighty_nine, zst_decompressed_size_times_eighty_nine
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_file_size_bytes_times_eighty_nine,
    zst_decompressed_size_times_eighty_nine,
)

_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_MINIMAL = str(_DIR / "minimal-synthetic.zst")
_TEXT = str(_DIR / "text-compressed.zst")
_BLOCK128 = str(_DIR / "block-128k.zst")


# --- zst_file_size_bytes_times_eighty_nine ---

class TestZstFileSizeBytesTimesEightyNine:
    def test_returns_int_minimal(self):
        result = zst_file_size_bytes_times_eighty_nine(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative_minimal(self):
        result = zst_file_size_bytes_times_eighty_nine(_MINIMAL)
        assert result >= 0

    def test_divisible_by_89_minimal(self):
        result = zst_file_size_bytes_times_eighty_nine(_MINIMAL)
        assert result % 89 == 0

    def test_returns_int_text(self):
        result = zst_file_size_bytes_times_eighty_nine(_TEXT)
        assert isinstance(result, int)

    def test_divisible_by_89_text(self):
        result = zst_file_size_bytes_times_eighty_nine(_TEXT)
        assert result % 89 == 0

    def test_block128_gte_minimal(self):
        r_min = zst_file_size_bytes_times_eighty_nine(_MINIMAL)
        r_big = zst_file_size_bytes_times_eighty_nine(_BLOCK128)
        assert r_big >= r_min


# --- zst_decompressed_size_times_eighty_nine ---

class TestZstDecompressedSizeTimesEightyNine:
    def test_returns_int_minimal(self):
        result = zst_decompressed_size_times_eighty_nine(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative_minimal(self):
        result = zst_decompressed_size_times_eighty_nine(_MINIMAL)
        assert result >= 0

    def test_divisible_by_89_minimal(self):
        result = zst_decompressed_size_times_eighty_nine(_MINIMAL)
        assert result % 89 == 0

    def test_returns_int_text(self):
        result = zst_decompressed_size_times_eighty_nine(_TEXT)
        assert isinstance(result, int)

    def test_divisible_by_89_text(self):
        result = zst_decompressed_size_times_eighty_nine(_TEXT)
        assert result % 89 == 0

    def test_returns_int_block128(self):
        result = zst_decompressed_size_times_eighty_nine(_BLOCK128)
        assert isinstance(result, int)

    def test_divisible_by_89_block128(self):
        result = zst_decompressed_size_times_eighty_nine(_BLOCK128)
        assert result % 89 == 0
