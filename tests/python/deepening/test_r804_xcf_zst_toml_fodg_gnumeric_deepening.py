"""Sprint R804 — ZST compound analytics deepening tests (Sprint 251)."""
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
    zst_compressed_mod_19_times_500_plus_decompressed_times_9_plus_file_size_times_25,
    zst_compressed_times_4_plus_decompressed_mod_50_times_30_plus_file_size_times_8,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod19Times500PlusDecompressedTimes9PlusFileSizeTimes25:
    def test_returns_int(self):
        result = zst_compressed_mod_19_times_500_plus_decompressed_times_9_plus_file_size_times_25(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_19_times_500_plus_decompressed_times_9_plus_file_size_times_25(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_19_times_500_plus_decompressed_times_9_plus_file_size_times_25(_ZST)
        assert result == 13310

    def test_string_path(self):
        result = zst_compressed_mod_19_times_500_plus_decompressed_times_9_plus_file_size_times_25(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_19_times_500_plus_decompressed_times_9_plus_file_size_times_25(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes4PlusDecompressedMod50Times30PlusFileSizeTimes8:
    def test_returns_int(self):
        result = zst_compressed_times_4_plus_decompressed_mod_50_times_30_plus_file_size_times_8(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_4_plus_decompressed_mod_50_times_30_plus_file_size_times_8(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_4_plus_decompressed_mod_50_times_30_plus_file_size_times_8(_ZST)
        assert result == 4464

    def test_string_path(self):
        result = zst_compressed_times_4_plus_decompressed_mod_50_times_30_plus_file_size_times_8(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_4_plus_decompressed_mod_50_times_30_plus_file_size_times_8(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
