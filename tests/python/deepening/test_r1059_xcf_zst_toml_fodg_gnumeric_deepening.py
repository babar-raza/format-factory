"""Sprint 506 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_443_times_4650_plus_decompressed_times_185_plus_file_size_times_192,
    zst_compressed_times_155_plus_decompressed_mod_940_times_830_plus_file_size_times_188,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1389174
FN2_EXPECTED = 416996


class TestZstCompressedMod443Times4650PlusDecompressedTimes185PlusFileSizeTimes192:
    def test_returns_int(self):
        result = zst_compressed_mod_443_times_4650_plus_decompressed_times_185_plus_file_size_times_192(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_443_times_4650_plus_decompressed_times_185_plus_file_size_times_192(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_443_times_4650_plus_decompressed_times_185_plus_file_size_times_192(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_443_times_4650_plus_decompressed_times_185_plus_file_size_times_192(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_443_times_4650_plus_decompressed_times_185_plus_file_size_times_192(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes155PlusDecompressedMod940Times830PlusFileSizeTimes188:
    def test_returns_int(self):
        result = zst_compressed_times_155_plus_decompressed_mod_940_times_830_plus_file_size_times_188(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_155_plus_decompressed_mod_940_times_830_plus_file_size_times_188(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_155_plus_decompressed_mod_940_times_830_plus_file_size_times_188(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_155_plus_decompressed_mod_940_times_830_plus_file_size_times_188(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_155_plus_decompressed_mod_940_times_830_plus_file_size_times_188(_SAMPLE)
        assert result == FN2_EXPECTED
