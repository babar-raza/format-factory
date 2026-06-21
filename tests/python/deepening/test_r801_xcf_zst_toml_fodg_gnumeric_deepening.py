"""Sprint R801 — ZST compound analytics deepening tests (Sprint 248)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

zstandard = None
try:
    import zstandard
except ImportError:
    pass

import pytest

if zstandard is None:
    pytest.skip("zstandard not installed", allow_module_level=True)

from src.python.zst.zst_codec import (
    zst_compressed_mod_13_times_400_plus_decompressed_times_7_plus_file_size_times_20,
    zst_compressed_times_6_plus_decompressed_mod_40_times_50_plus_file_size_times_3,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod13Times400PlusDecompressedTimes7PlusFileSizeTimes20:
    def test_returns_int(self):
        result = zst_compressed_mod_13_times_400_plus_decompressed_times_7_plus_file_size_times_20(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_13_times_400_plus_decompressed_times_7_plus_file_size_times_20(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_13_times_400_plus_decompressed_times_7_plus_file_size_times_20(_ZST)
        assert result == 12970

    def test_string_path(self):
        result = zst_compressed_mod_13_times_400_plus_decompressed_times_7_plus_file_size_times_20(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_13_times_400_plus_decompressed_times_7_plus_file_size_times_20(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes6PlusDecompressedMod40Times50PlusFileSizeTimes3:
    def test_returns_int(self):
        result = zst_compressed_times_6_plus_decompressed_mod_40_times_50_plus_file_size_times_3(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_6_plus_decompressed_mod_40_times_50_plus_file_size_times_3(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_6_plus_decompressed_mod_40_times_50_plus_file_size_times_3(_ZST)
        assert result == 3948

    def test_string_path(self):
        result = zst_compressed_times_6_plus_decompressed_mod_40_times_50_plus_file_size_times_3(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_6_plus_decompressed_mod_40_times_50_plus_file_size_times_3(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
