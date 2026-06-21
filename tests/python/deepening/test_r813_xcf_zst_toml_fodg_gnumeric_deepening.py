"""Sprint R813 — ZST compound analytics deepening tests (Sprint 260)."""
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
    zst_compressed_mod_43_times_250_plus_decompressed_times_15_plus_file_size_times_22,
    zst_compressed_times_7_plus_decompressed_mod_80_times_70_plus_file_size_times_16,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod43Times250PlusDecompressedTimes15PlusFileSizeTimes22:
    def test_returns_int(self):
        result = zst_compressed_mod_43_times_250_plus_decompressed_times_15_plus_file_size_times_22(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_43_times_250_plus_decompressed_times_15_plus_file_size_times_22(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_43_times_250_plus_decompressed_times_15_plus_file_size_times_22(_ZST)
        assert result == 15334

    def test_string_path(self):
        result = zst_compressed_mod_43_times_250_plus_decompressed_times_15_plus_file_size_times_22(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_43_times_250_plus_decompressed_times_15_plus_file_size_times_22(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes7PlusDecompressedMod80Times70PlusFileSizeTimes16:
    def test_returns_int(self):
        result = zst_compressed_times_7_plus_decompressed_mod_80_times_70_plus_file_size_times_16(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_7_plus_decompressed_mod_80_times_70_plus_file_size_times_16(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_7_plus_decompressed_mod_80_times_70_plus_file_size_times_16(_ZST)
        assert result == 11156

    def test_string_path(self):
        result = zst_compressed_times_7_plus_decompressed_mod_80_times_70_plus_file_size_times_16(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_7_plus_decompressed_mod_80_times_70_plus_file_size_times_16(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
