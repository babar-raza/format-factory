"""Sprint 515 - ZST deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

try:
    import zstandard  # noqa: F401
except ImportError:
    pytest.skip("zstandard not installed", allow_module_level=True)

from src.python.zst import (
    zst_compressed_mod_461_times_4800_plus_decompressed_times_191_plus_file_size_times_198,
    zst_compressed_times_161_plus_decompressed_mod_970_times_860_plus_file_size_times_194,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1433946
FN2_EXPECTED = 431960


class TestZstCompressedMod461Times4800PlusDecompressedTimes191PlusFileSizeTimes198:
    def test_returns_int(self):
        result = zst_compressed_mod_461_times_4800_plus_decompressed_times_191_plus_file_size_times_198(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_461_times_4800_plus_decompressed_times_191_plus_file_size_times_198(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_461_times_4800_plus_decompressed_times_191_plus_file_size_times_198(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_461_times_4800_plus_decompressed_times_191_plus_file_size_times_198(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_461_times_4800_plus_decompressed_times_191_plus_file_size_times_198(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes161PlusDecompressedMod970Times860PlusFileSizeTimes194:
    def test_returns_int(self):
        result = zst_compressed_times_161_plus_decompressed_mod_970_times_860_plus_file_size_times_194(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_161_plus_decompressed_mod_970_times_860_plus_file_size_times_194(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_161_plus_decompressed_mod_970_times_860_plus_file_size_times_194(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_161_plus_decompressed_mod_970_times_860_plus_file_size_times_194(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_161_plus_decompressed_mod_970_times_860_plus_file_size_times_194(_SAMPLE)
        assert result == FN2_EXPECTED
