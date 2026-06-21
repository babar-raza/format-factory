"""Sprint 383 — ZST deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

try:
    import zstandard  # noqa: F401
except ImportError:
    import pytest
    pytest.skip("zstandard not installed", allow_module_level=True)

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_compressed_mod_227_times_2450_plus_decompressed_times_101_plus_file_size_times_108,
    zst_compressed_times_71_plus_decompressed_mod_510_times_400_plus_file_size_times_102,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 179016
FN2_EXPECTED = 203056


class TestZstCompressedMod227Times2450PlusDecompressedTimes101PlusFileSizeTimes108:
    def test_returns_int(self):
        result = zst_compressed_mod_227_times_2450_plus_decompressed_times_101_plus_file_size_times_108(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_227_times_2450_plus_decompressed_times_101_plus_file_size_times_108(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_227_times_2450_plus_decompressed_times_101_plus_file_size_times_108(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_227_times_2450_plus_decompressed_times_101_plus_file_size_times_108(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_227_times_2450_plus_decompressed_times_101_plus_file_size_times_108(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes71PlusDecompressedMod510Times400PlusFileSizeTimes102:
    def test_returns_int(self):
        result = zst_compressed_times_71_plus_decompressed_mod_510_times_400_plus_file_size_times_102(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_71_plus_decompressed_mod_510_times_400_plus_file_size_times_102(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_71_plus_decompressed_mod_510_times_400_plus_file_size_times_102(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_71_plus_decompressed_mod_510_times_400_plus_file_size_times_102(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_71_plus_decompressed_mod_510_times_400_plus_file_size_times_102(_SAMPLE)
        assert result == FN2_EXPECTED
