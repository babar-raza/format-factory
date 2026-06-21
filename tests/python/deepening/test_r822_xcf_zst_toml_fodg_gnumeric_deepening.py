"""Sprint R822 — ZST compound analytics deepening tests (Sprint 269)."""
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
    zst_compressed_mod_59_times_450_plus_decompressed_times_21_plus_file_size_times_28,
    zst_compressed_times_10_plus_decompressed_mod_110_times_95_plus_file_size_times_22,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod59Times450PlusDecompressedTimes21PlusFileSizeTimes28:
    def test_returns_int(self):
        result = zst_compressed_mod_59_times_450_plus_decompressed_times_21_plus_file_size_times_28(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_59_times_450_plus_decompressed_times_21_plus_file_size_times_28(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_59_times_450_plus_decompressed_times_21_plus_file_size_times_28(_ZST)
        assert result == 32006

    def test_string_path(self):
        result = zst_compressed_mod_59_times_450_plus_decompressed_times_21_plus_file_size_times_28(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_59_times_450_plus_decompressed_times_21_plus_file_size_times_28(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes10PlusDecompressedMod110Times95PlusFileSizeTimes22:
    def test_returns_int(self):
        result = zst_compressed_times_10_plus_decompressed_mod_110_times_95_plus_file_size_times_22(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_10_plus_decompressed_mod_110_times_95_plus_file_size_times_22(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_10_plus_decompressed_mod_110_times_95_plus_file_size_times_22(_ZST)
        assert result == 14404

    def test_string_path(self):
        result = zst_compressed_times_10_plus_decompressed_mod_110_times_95_plus_file_size_times_22(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_10_plus_decompressed_mod_110_times_95_plus_file_size_times_22(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
