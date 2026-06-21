"""Sprint R885 — ZST compound analytics deepening tests (Sprint 332)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

try:
    import zstandard  # noqa: F401
except ImportError:
    pytest.skip("zstandard not installed", allow_module_level=True)

from src.python.zst import (
    zst_compressed_mod_173_times_1500_plus_decompressed_times_63_plus_file_size_times_70,
    zst_compressed_times_33_plus_decompressed_mod_320_times_210_plus_file_size_times_64,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod173Times1500PlusDecompressedTimes63PlusFileSizeTimes70:
    def test_returns_int(self):
        result = zst_compressed_mod_173_times_1500_plus_decompressed_times_63_plus_file_size_times_70(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_173_times_1500_plus_decompressed_times_63_plus_file_size_times_70(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_173_times_1500_plus_decompressed_times_63_plus_file_size_times_70(_ZST)
        assert result == 192110

    def test_string_path(self):
        result = zst_compressed_mod_173_times_1500_plus_decompressed_times_63_plus_file_size_times_70(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_173_times_1500_plus_decompressed_times_63_plus_file_size_times_70(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes33PlusDecompressedMod320Times210PlusFileSizeTimes64:
    def test_returns_int(self):
        result = zst_compressed_times_33_plus_decompressed_mod_320_times_210_plus_file_size_times_64(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_33_plus_decompressed_mod_320_times_210_plus_file_size_times_64(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_33_plus_decompressed_mod_320_times_210_plus_file_size_times_64(_ZST)
        assert result == 41084

    def test_string_path(self):
        result = zst_compressed_times_33_plus_decompressed_mod_320_times_210_plus_file_size_times_64(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_33_plus_decompressed_mod_320_times_210_plus_file_size_times_64(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
