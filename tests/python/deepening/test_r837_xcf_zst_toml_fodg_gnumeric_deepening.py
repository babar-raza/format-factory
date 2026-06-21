"""Sprint R837 — ZST compound analytics deepening tests (Sprint 284)."""
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
    zst_compressed_mod_79_times_700_plus_decompressed_times_31_plus_file_size_times_38,
    zst_compressed_times_15_plus_decompressed_mod_160_times_120_plus_file_size_times_32,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod79Times700PlusDecompressedTimes31PlusFileSizeTimes38:
    def test_returns_int(self):
        result = zst_compressed_mod_79_times_700_plus_decompressed_times_31_plus_file_size_times_38(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_79_times_700_plus_decompressed_times_31_plus_file_size_times_38(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_79_times_700_plus_decompressed_times_31_plus_file_size_times_38(_ZST)
        assert result == 46926

    def test_string_path(self):
        result = zst_compressed_mod_79_times_700_plus_decompressed_times_31_plus_file_size_times_38(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_79_times_700_plus_decompressed_times_31_plus_file_size_times_38(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes15PlusDecompressedMod160Times120PlusFileSizeTimes32:
    def test_returns_int(self):
        result = zst_compressed_times_15_plus_decompressed_mod_160_times_120_plus_file_size_times_32(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_15_plus_decompressed_mod_160_times_120_plus_file_size_times_32(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_15_plus_decompressed_mod_160_times_120_plus_file_size_times_32(_ZST)
        assert result == 21184

    def test_string_path(self):
        result = zst_compressed_times_15_plus_decompressed_mod_160_times_120_plus_file_size_times_32(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_15_plus_decompressed_mod_160_times_120_plus_file_size_times_32(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
