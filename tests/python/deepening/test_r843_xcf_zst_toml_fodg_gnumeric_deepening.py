"""Sprint R843 — ZST compound analytics deepening tests (Sprint 290)."""
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
    zst_compressed_mod_89_times_800_plus_decompressed_times_35_plus_file_size_times_42,
    zst_compressed_times_17_plus_decompressed_mod_180_times_130_plus_file_size_times_36,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod89Times800PlusDecompressedTimes35PlusFileSizeTimes42:
    def test_returns_int(self):
        result = zst_compressed_mod_89_times_800_plus_decompressed_times_35_plus_file_size_times_42(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_89_times_800_plus_decompressed_times_35_plus_file_size_times_42(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_89_times_800_plus_decompressed_times_35_plus_file_size_times_42(_ZST)
        assert result == 29074

    def test_string_path(self):
        result = zst_compressed_mod_89_times_800_plus_decompressed_times_35_plus_file_size_times_42(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_89_times_800_plus_decompressed_times_35_plus_file_size_times_42(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes17PlusDecompressedMod180Times130PlusFileSizeTimes36:
    def test_returns_int(self):
        result = zst_compressed_times_17_plus_decompressed_mod_180_times_130_plus_file_size_times_36(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_17_plus_decompressed_mod_180_times_130_plus_file_size_times_36(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_17_plus_decompressed_mod_180_times_130_plus_file_size_times_36(_ZST)
        assert result == 18316

    def test_string_path(self):
        result = zst_compressed_times_17_plus_decompressed_mod_180_times_130_plus_file_size_times_36(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_17_plus_decompressed_mod_180_times_130_plus_file_size_times_36(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
