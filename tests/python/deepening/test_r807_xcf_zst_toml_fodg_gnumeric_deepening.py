"""Sprint R807 — ZST compound analytics deepening tests (Sprint 254)."""
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
    zst_compressed_mod_31_times_200_plus_decompressed_times_11_plus_file_size_times_15,
    zst_compressed_times_5_plus_decompressed_mod_60_times_40_plus_file_size_times_12,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod31Times200PlusDecompressedTimes11PlusFileSizeTimes15:
    def test_returns_int(self):
        result = zst_compressed_mod_31_times_200_plus_decompressed_times_11_plus_file_size_times_15(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_31_times_200_plus_decompressed_times_11_plus_file_size_times_15(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_31_times_200_plus_decompressed_times_11_plus_file_size_times_15(_ZST)
        assert result == 13170

    def test_string_path(self):
        result = zst_compressed_mod_31_times_200_plus_decompressed_times_11_plus_file_size_times_15(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_31_times_200_plus_decompressed_times_11_plus_file_size_times_15(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes5PlusDecompressedMod60Times40PlusFileSizeTimes12:
    def test_returns_int(self):
        result = zst_compressed_times_5_plus_decompressed_mod_60_times_40_plus_file_size_times_12(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_5_plus_decompressed_mod_60_times_40_plus_file_size_times_12(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_5_plus_decompressed_mod_60_times_40_plus_file_size_times_12(_ZST)
        assert result == 5824

    def test_string_path(self):
        result = zst_compressed_times_5_plus_decompressed_mod_60_times_40_plus_file_size_times_12(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_5_plus_decompressed_mod_60_times_40_plus_file_size_times_12(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
