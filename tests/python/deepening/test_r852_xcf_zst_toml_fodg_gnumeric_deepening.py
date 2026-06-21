"""Sprint R852 — ZST compound analytics deepening tests (Sprint 299)."""
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
    zst_compressed_mod_109_times_950_plus_decompressed_times_41_plus_file_size_times_48,
    zst_compressed_times_21_plus_decompressed_mod_210_times_150_plus_file_size_times_42,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod109Times950PlusDecompressedTimes41PlusFileSizeTimes48:
    def test_returns_int(self):
        result = zst_compressed_mod_109_times_950_plus_decompressed_times_41_plus_file_size_times_48(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_109_times_950_plus_decompressed_times_41_plus_file_size_times_48(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_109_times_950_plus_decompressed_times_41_plus_file_size_times_48(_ZST)
        assert result == 80346

    def test_string_path(self):
        result = zst_compressed_mod_109_times_950_plus_decompressed_times_41_plus_file_size_times_48(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_109_times_950_plus_decompressed_times_41_plus_file_size_times_48(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes21PlusDecompressedMod210Times150PlusFileSizeTimes42:
    def test_returns_int(self):
        result = zst_compressed_times_21_plus_decompressed_mod_210_times_150_plus_file_size_times_42(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_21_plus_decompressed_mod_210_times_150_plus_file_size_times_42(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_21_plus_decompressed_mod_210_times_150_plus_file_size_times_42(_ZST)
        assert result == 44136

    def test_string_path(self):
        result = zst_compressed_times_21_plus_decompressed_mod_210_times_150_plus_file_size_times_42(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_21_plus_decompressed_mod_210_times_150_plus_file_size_times_42(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
