"""Sprint R810 — ZST compound analytics deepening tests (Sprint 257)."""
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
    zst_compressed_mod_41_times_300_plus_decompressed_times_13_plus_file_size_times_18,
    zst_compressed_times_6_plus_decompressed_mod_70_times_60_plus_file_size_times_14,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod41Times300PlusDecompressedTimes13PlusFileSizeTimes18:
    def test_returns_int(self):
        result = zst_compressed_mod_41_times_300_plus_decompressed_times_13_plus_file_size_times_18(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_41_times_300_plus_decompressed_times_13_plus_file_size_times_18(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_41_times_300_plus_decompressed_times_13_plus_file_size_times_18(_ZST)
        assert result == 17766

    def test_string_path(self):
        result = zst_compressed_mod_41_times_300_plus_decompressed_times_13_plus_file_size_times_18(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_41_times_300_plus_decompressed_times_13_plus_file_size_times_18(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes6PlusDecompressedMod70Times60PlusFileSizeTimes14:
    def test_returns_int(self):
        result = zst_compressed_times_6_plus_decompressed_mod_70_times_60_plus_file_size_times_14(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_6_plus_decompressed_mod_70_times_60_plus_file_size_times_14(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_6_plus_decompressed_mod_70_times_60_plus_file_size_times_14(_ZST)
        assert result == 7840

    def test_string_path(self):
        result = zst_compressed_times_6_plus_decompressed_mod_70_times_60_plus_file_size_times_14(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_6_plus_decompressed_mod_70_times_60_plus_file_size_times_14(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
