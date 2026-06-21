"""Sprint R882 — ZST compound analytics deepening tests (Sprint 329)."""
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
    zst_compressed_mod_173_times_1450_plus_decompressed_times_61_plus_file_size_times_68,
    zst_compressed_times_31_plus_decompressed_mod_310_times_200_plus_file_size_times_62,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod173Times1450PlusDecompressedTimes61PlusFileSizeTimes68:
    def test_returns_int(self):
        result = zst_compressed_mod_173_times_1450_plus_decompressed_times_61_plus_file_size_times_68(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_173_times_1450_plus_decompressed_times_61_plus_file_size_times_68(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_173_times_1450_plus_decompressed_times_61_plus_file_size_times_68(_ZST)
        assert result == 185836

    def test_string_path(self):
        result = zst_compressed_mod_173_times_1450_plus_decompressed_times_61_plus_file_size_times_68(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_173_times_1450_plus_decompressed_times_61_plus_file_size_times_68(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes31PlusDecompressedMod310Times200PlusFileSizeTimes62:
    def test_returns_int(self):
        result = zst_compressed_times_31_plus_decompressed_mod_310_times_200_plus_file_size_times_62(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_31_plus_decompressed_mod_310_times_200_plus_file_size_times_62(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_31_plus_decompressed_mod_310_times_200_plus_file_size_times_62(_ZST)
        assert result == 41296

    def test_string_path(self):
        result = zst_compressed_times_31_plus_decompressed_mod_310_times_200_plus_file_size_times_62(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_31_plus_decompressed_mod_310_times_200_plus_file_size_times_62(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
