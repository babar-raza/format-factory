"""Sprint R864 — ZST compound analytics deepening tests (Sprint 311)."""
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
    zst_compressed_mod_137_times_1150_plus_decompressed_times_49_plus_file_size_times_56,
    zst_compressed_times_25_plus_decompressed_mod_250_times_170_plus_file_size_times_50,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod137Times1150PlusDecompressedTimes49PlusFileSizeTimes56:
    def test_returns_int(self):
        result = zst_compressed_mod_137_times_1150_plus_decompressed_times_49_plus_file_size_times_56(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_137_times_1150_plus_decompressed_times_49_plus_file_size_times_56(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_137_times_1150_plus_decompressed_times_49_plus_file_size_times_56(_ZST)
        assert result == 189592

    def test_string_path(self):
        result = zst_compressed_mod_137_times_1150_plus_decompressed_times_49_plus_file_size_times_56(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_137_times_1150_plus_decompressed_times_49_plus_file_size_times_56(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes25PlusDecompressedMod250Times170PlusFileSizeTimes50:
    def test_returns_int(self):
        result = zst_compressed_times_25_plus_decompressed_mod_250_times_170_plus_file_size_times_50(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_25_plus_decompressed_mod_250_times_170_plus_file_size_times_50(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_25_plus_decompressed_mod_250_times_170_plus_file_size_times_50(_ZST)
        assert result == 44200

    def test_string_path(self):
        result = zst_compressed_times_25_plus_decompressed_mod_250_times_170_plus_file_size_times_50(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_25_plus_decompressed_mod_250_times_170_plus_file_size_times_50(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
