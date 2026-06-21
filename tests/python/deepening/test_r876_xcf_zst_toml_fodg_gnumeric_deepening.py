"""Sprint R876 — ZST compound analytics deepening tests (Sprint 323)."""
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
    pytest.skip("python-zstandard not installed", allow_module_level=True)

from src.python.zst import (
    zst_compressed_mod_163_times_1350_plus_decompressed_times_57_plus_file_size_times_64,
    zst_compressed_times_29_plus_decompressed_mod_290_times_190_plus_file_size_times_58,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod163Times1350PlusDecompressedTimes57PlusFileSizeTimes64:
    def test_returns_int(self):
        result = zst_compressed_mod_163_times_1350_plus_decompressed_times_57_plus_file_size_times_64(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_163_times_1350_plus_decompressed_times_57_plus_file_size_times_64(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_163_times_1350_plus_decompressed_times_57_plus_file_size_times_64(_ZST)
        assert result == 186788

    def test_string_path(self):
        result = zst_compressed_mod_163_times_1350_plus_decompressed_times_57_plus_file_size_times_64(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_163_times_1350_plus_decompressed_times_57_plus_file_size_times_64(
            SAMPLES / "zst" / "valid" / "text-compressed.zst"
        )
        assert isinstance(result, int)


class TestZstCompressedTimes29PlusDecompressedMod290Times190PlusFileSizeTimes58:
    def test_returns_int(self):
        result = zst_compressed_times_29_plus_decompressed_mod_290_times_190_plus_file_size_times_58(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_29_plus_decompressed_mod_290_times_190_plus_file_size_times_58(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_29_plus_decompressed_mod_290_times_190_plus_file_size_times_58(_ZST)
        assert result == 42664

    def test_string_path(self):
        result = zst_compressed_times_29_plus_decompressed_mod_290_times_190_plus_file_size_times_58(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_29_plus_decompressed_mod_290_times_190_plus_file_size_times_58(
            SAMPLES / "zst" / "valid" / "text-compressed.zst"
        )
        assert isinstance(result, int)
