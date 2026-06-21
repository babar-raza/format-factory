"""Sprint R819 — ZST compound analytics deepening tests (Sprint 266)."""
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
    zst_compressed_mod_53_times_400_plus_decompressed_times_19_plus_file_size_times_26,
    zst_compressed_times_9_plus_decompressed_mod_100_times_90_plus_file_size_times_20,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod53Times400PlusDecompressedTimes19PlusFileSizeTimes26:
    def test_returns_int(self):
        result = zst_compressed_mod_53_times_400_plus_decompressed_times_19_plus_file_size_times_26(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_53_times_400_plus_decompressed_times_19_plus_file_size_times_26(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_53_times_400_plus_decompressed_times_19_plus_file_size_times_26(_ZST)
        assert result == 17282

    def test_string_path(self):
        result = zst_compressed_mod_53_times_400_plus_decompressed_times_19_plus_file_size_times_26(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_53_times_400_plus_decompressed_times_19_plus_file_size_times_26(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes9PlusDecompressedMod100Times90PlusFileSizeTimes20:
    def test_returns_int(self):
        result = zst_compressed_times_9_plus_decompressed_mod_100_times_90_plus_file_size_times_20(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_9_plus_decompressed_mod_100_times_90_plus_file_size_times_20(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_9_plus_decompressed_mod_100_times_90_plus_file_size_times_20(_ZST)
        assert result == 15988

    def test_string_path(self):
        result = zst_compressed_times_9_plus_decompressed_mod_100_times_90_plus_file_size_times_20(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_9_plus_decompressed_mod_100_times_90_plus_file_size_times_20(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
