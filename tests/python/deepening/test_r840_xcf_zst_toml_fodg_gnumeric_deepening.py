"""Sprint R840 — ZST compound analytics deepening tests (Sprint 287)."""
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
    zst_compressed_mod_83_times_750_plus_decompressed_times_33_plus_file_size_times_40,
    zst_compressed_times_16_plus_decompressed_mod_170_times_125_plus_file_size_times_34,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod83Times750PlusDecompressedTimes33PlusFileSizeTimes40:
    def test_returns_int(self):
        result = zst_compressed_mod_83_times_750_plus_decompressed_times_33_plus_file_size_times_40(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_83_times_750_plus_decompressed_times_33_plus_file_size_times_40(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_83_times_750_plus_decompressed_times_33_plus_file_size_times_40(_ZST)
        assert result == 41000

    def test_string_path(self):
        result = zst_compressed_mod_83_times_750_plus_decompressed_times_33_plus_file_size_times_40(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_83_times_750_plus_decompressed_times_33_plus_file_size_times_40(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes16PlusDecompressedMod170Times125PlusFileSizeTimes34:
    def test_returns_int(self):
        result = zst_compressed_times_16_plus_decompressed_mod_170_times_125_plus_file_size_times_34(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_16_plus_decompressed_mod_170_times_125_plus_file_size_times_34(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_16_plus_decompressed_mod_170_times_125_plus_file_size_times_34(_ZST)
        assert result == 19850

    def test_string_path(self):
        result = zst_compressed_times_16_plus_decompressed_mod_170_times_125_plus_file_size_times_34(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_16_plus_decompressed_mod_170_times_125_plus_file_size_times_34(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
