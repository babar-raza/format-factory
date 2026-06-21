"""Sprint R894 — ZST compound analytics deepening tests (Sprint 341)."""
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
    zst_compressed_mod_183_times_1650_plus_decompressed_times_69_plus_file_size_times_76,
    zst_compressed_times_39_plus_decompressed_mod_350_times_240_plus_file_size_times_70,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod183Times1650PlusDecompressedTimes69PlusFileSizeTimes76:
    def test_returns_int(self):
        result = zst_compressed_mod_183_times_1650_plus_decompressed_times_69_plus_file_size_times_76(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_183_times_1650_plus_decompressed_times_69_plus_file_size_times_76(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_183_times_1650_plus_decompressed_times_69_plus_file_size_times_76(_ZST)
        assert result == 194432

    def test_string_path(self):
        result = zst_compressed_mod_183_times_1650_plus_decompressed_times_69_plus_file_size_times_76(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_183_times_1650_plus_decompressed_times_69_plus_file_size_times_76(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes39PlusDecompressedMod350Times240PlusFileSizeTimes70:
    def test_returns_int(self):
        result = zst_compressed_times_39_plus_decompressed_mod_350_times_240_plus_file_size_times_70(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_39_plus_decompressed_mod_350_times_240_plus_file_size_times_70(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_39_plus_decompressed_mod_350_times_240_plus_file_size_times_70(_ZST)
        assert result == 39248

    def test_string_path(self):
        result = zst_compressed_times_39_plus_decompressed_mod_350_times_240_plus_file_size_times_70(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_39_plus_decompressed_mod_350_times_240_plus_file_size_times_70(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
