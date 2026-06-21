"""Sprint R825 — ZST compound analytics deepening tests (Sprint 272)."""
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
    zst_compressed_mod_61_times_500_plus_decompressed_times_23_plus_file_size_times_30,
    zst_compressed_times_11_plus_decompressed_mod_120_times_100_plus_file_size_times_24,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod61Times500PlusDecompressedTimes23PlusFileSizeTimes30:
    def test_returns_int(self):
        result = zst_compressed_mod_61_times_500_plus_decompressed_times_23_plus_file_size_times_30(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_61_times_500_plus_decompressed_times_23_plus_file_size_times_30(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_61_times_500_plus_decompressed_times_23_plus_file_size_times_30(_ZST)
        assert result == 31130

    def test_string_path(self):
        result = zst_compressed_mod_61_times_500_plus_decompressed_times_23_plus_file_size_times_30(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_61_times_500_plus_decompressed_times_23_plus_file_size_times_30(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes11PlusDecompressedMod120Times100PlusFileSizeTimes24:
    def test_returns_int(self):
        result = zst_compressed_times_11_plus_decompressed_mod_120_times_100_plus_file_size_times_24(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_11_plus_decompressed_mod_120_times_100_plus_file_size_times_24(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_11_plus_decompressed_mod_120_times_100_plus_file_size_times_24(_ZST)
        assert result == 12520

    def test_string_path(self):
        result = zst_compressed_times_11_plus_decompressed_mod_120_times_100_plus_file_size_times_24(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_11_plus_decompressed_mod_120_times_100_plus_file_size_times_24(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
