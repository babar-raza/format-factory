"""Sprint R867 — ZST compound analytics deepening tests (Sprint 314)."""
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
    zst_compressed_mod_149_times_1200_plus_decompressed_times_51_plus_file_size_times_58,
    zst_compressed_times_26_plus_decompressed_mod_260_times_175_plus_file_size_times_52,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod149Times1200PlusDecompressedTimes51PlusFileSizeTimes58:
    def test_returns_int(self):
        result = zst_compressed_mod_149_times_1200_plus_decompressed_times_51_plus_file_size_times_58(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_149_times_1200_plus_decompressed_times_51_plus_file_size_times_58(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_149_times_1200_plus_decompressed_times_51_plus_file_size_times_58(_ZST)
        assert result == 183266

    def test_string_path(self):
        result = zst_compressed_mod_149_times_1200_plus_decompressed_times_51_plus_file_size_times_58(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_149_times_1200_plus_decompressed_times_51_plus_file_size_times_58(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes26PlusDecompressedMod260Times175PlusFileSizeTimes52:
    def test_returns_int(self):
        result = zst_compressed_times_26_plus_decompressed_mod_260_times_175_plus_file_size_times_52(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_26_plus_decompressed_mod_260_times_175_plus_file_size_times_52(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_26_plus_decompressed_mod_260_times_175_plus_file_size_times_52(_ZST)
        assert result == 43966

    def test_string_path(self):
        result = zst_compressed_times_26_plus_decompressed_mod_260_times_175_plus_file_size_times_52(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_26_plus_decompressed_mod_260_times_175_plus_file_size_times_52(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
