"""Sprint R816 — ZST compound analytics deepening tests (Sprint 263)."""
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
    zst_compressed_mod_47_times_350_plus_decompressed_times_17_plus_file_size_times_24,
    zst_compressed_times_8_plus_decompressed_mod_90_times_80_plus_file_size_times_18,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod47Times350PlusDecompressedTimes17PlusFileSizeTimes24:
    def test_returns_int(self):
        result = zst_compressed_mod_47_times_350_plus_decompressed_times_17_plus_file_size_times_24(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_47_times_350_plus_decompressed_times_17_plus_file_size_times_24(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_47_times_350_plus_decompressed_times_17_plus_file_size_times_24(_ZST)
        assert result == 26108

    def test_string_path(self):
        result = zst_compressed_mod_47_times_350_plus_decompressed_times_17_plus_file_size_times_24(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_47_times_350_plus_decompressed_times_17_plus_file_size_times_24(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes8PlusDecompressedMod90Times80PlusFileSizeTimes18:
    def test_returns_int(self):
        result = zst_compressed_times_8_plus_decompressed_mod_90_times_80_plus_file_size_times_18(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_8_plus_decompressed_mod_90_times_80_plus_file_size_times_18(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_8_plus_decompressed_mod_90_times_80_plus_file_size_times_18(_ZST)
        assert result == 9472

    def test_string_path(self):
        result = zst_compressed_times_8_plus_decompressed_mod_90_times_80_plus_file_size_times_18(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_8_plus_decompressed_mod_90_times_80_plus_file_size_times_18(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
