"""Sprint 365 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_213_times_2150_plus_decompressed_times_89_plus_file_size_times_96,
    zst_compressed_times_59_plus_decompressed_mod_450_times_340_plus_file_size_times_90,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 187672
FN2_EXPECTED = 173128


class TestZstCompressedMod213Times2150PlusDecompressedTimes89PlusFileSizeTimes96:
    def test_returns_int(self):
        result = zst_compressed_mod_213_times_2150_plus_decompressed_times_89_plus_file_size_times_96(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_213_times_2150_plus_decompressed_times_89_plus_file_size_times_96(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_213_times_2150_plus_decompressed_times_89_plus_file_size_times_96(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_213_times_2150_plus_decompressed_times_89_plus_file_size_times_96(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_213_times_2150_plus_decompressed_times_89_plus_file_size_times_96(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes59PlusDecompressedMod450Times340PlusFileSizeTimes90:
    def test_returns_int(self):
        result = zst_compressed_times_59_plus_decompressed_mod_450_times_340_plus_file_size_times_90(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_59_plus_decompressed_mod_450_times_340_plus_file_size_times_90(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_59_plus_decompressed_mod_450_times_340_plus_file_size_times_90(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_59_plus_decompressed_mod_450_times_340_plus_file_size_times_90(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_59_plus_decompressed_mod_450_times_340_plus_file_size_times_90(_SAMPLE)
        assert result == FN2_EXPECTED
