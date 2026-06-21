"""Sprint R834 — ZST compound analytics deepening tests (Sprint 281)."""
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
    zst_compressed_mod_73_times_650_plus_decompressed_times_29_plus_file_size_times_36,
    zst_compressed_times_14_plus_decompressed_mod_150_times_115_plus_file_size_times_30,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod73Times650PlusDecompressedTimes29PlusFileSizeTimes36:
    def test_returns_int(self):
        result = zst_compressed_mod_73_times_650_plus_decompressed_times_29_plus_file_size_times_36(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_73_times_650_plus_decompressed_times_29_plus_file_size_times_36(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_73_times_650_plus_decompressed_times_29_plus_file_size_times_36(_ZST)
        assert result == 55552

    def test_string_path(self):
        result = zst_compressed_mod_73_times_650_plus_decompressed_times_29_plus_file_size_times_36(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_73_times_650_plus_decompressed_times_29_plus_file_size_times_36(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes14PlusDecompressedMod150Times115PlusFileSizeTimes30:
    def test_returns_int(self):
        result = zst_compressed_times_14_plus_decompressed_mod_150_times_115_plus_file_size_times_30(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_14_plus_decompressed_mod_150_times_115_plus_file_size_times_30(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_14_plus_decompressed_mod_150_times_115_plus_file_size_times_30(_ZST)
        assert result == 22318

    def test_string_path(self):
        result = zst_compressed_times_14_plus_decompressed_mod_150_times_115_plus_file_size_times_30(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_14_plus_decompressed_mod_150_times_115_plus_file_size_times_30(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
