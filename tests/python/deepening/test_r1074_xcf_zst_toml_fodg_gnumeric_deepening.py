"""Sprint 521 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_467_times_4900_plus_decompressed_times_195_plus_file_size_times_202,
    zst_compressed_times_165_plus_decompressed_mod_990_times_880_plus_file_size_times_198,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1463794
FN2_EXPECTED = 441936


class TestZstCompressedMod467Times4900PlusDecompressedTimes195PlusFileSizeTimes202:
    def test_returns_int(self):
        result = zst_compressed_mod_467_times_4900_plus_decompressed_times_195_plus_file_size_times_202(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_467_times_4900_plus_decompressed_times_195_plus_file_size_times_202(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_467_times_4900_plus_decompressed_times_195_plus_file_size_times_202(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_467_times_4900_plus_decompressed_times_195_plus_file_size_times_202(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_467_times_4900_plus_decompressed_times_195_plus_file_size_times_202(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes165PlusDecompressedMod990Times880PlusFileSizeTimes198:
    def test_returns_int(self):
        result = zst_compressed_times_165_plus_decompressed_mod_990_times_880_plus_file_size_times_198(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_165_plus_decompressed_mod_990_times_880_plus_file_size_times_198(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_165_plus_decompressed_mod_990_times_880_plus_file_size_times_198(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_165_plus_decompressed_mod_990_times_880_plus_file_size_times_198(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_165_plus_decompressed_mod_990_times_880_plus_file_size_times_198(_SAMPLE)
        assert result == FN2_EXPECTED
