"""Sprint R855 — ZST compound analytics deepening tests (Sprint 302)."""
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
    zst_compressed_mod_113_times_1000_plus_decompressed_times_43_plus_file_size_times_50,
    zst_compressed_times_22_plus_decompressed_mod_220_times_155_plus_file_size_times_44,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod113Times1000PlusDecompressedTimes43PlusFileSizeTimes50:
    def test_returns_int(self):
        result = zst_compressed_mod_113_times_1000_plus_decompressed_times_43_plus_file_size_times_50(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_113_times_1000_plus_decompressed_times_43_plus_file_size_times_50(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_113_times_1000_plus_decompressed_times_43_plus_file_size_times_50(_ZST)
        assert result == 76370

    def test_string_path(self):
        result = zst_compressed_mod_113_times_1000_plus_decompressed_times_43_plus_file_size_times_50(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_113_times_1000_plus_decompressed_times_43_plus_file_size_times_50(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes22PlusDecompressedMod220Times155PlusFileSizeTimes44:
    def test_returns_int(self):
        result = zst_compressed_times_22_plus_decompressed_mod_220_times_155_plus_file_size_times_44(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_22_plus_decompressed_mod_220_times_155_plus_file_size_times_44(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_22_plus_decompressed_mod_220_times_155_plus_file_size_times_44(_ZST)
        assert result == 44302

    def test_string_path(self):
        result = zst_compressed_times_22_plus_decompressed_mod_220_times_155_plus_file_size_times_44(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_22_plus_decompressed_mod_220_times_155_plus_file_size_times_44(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
