"""Sprint R828 — ZST compound analytics deepening tests (Sprint 275)."""
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
    zst_compressed_mod_67_times_550_plus_decompressed_times_25_plus_file_size_times_32,
    zst_compressed_times_12_plus_decompressed_mod_130_times_105_plus_file_size_times_26,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod67Times550PlusDecompressedTimes25PlusFileSizeTimes32:
    def test_returns_int(self):
        result = zst_compressed_mod_67_times_550_plus_decompressed_times_25_plus_file_size_times_32(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_67_times_550_plus_decompressed_times_25_plus_file_size_times_32(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_67_times_550_plus_decompressed_times_25_plus_file_size_times_32(_ZST)
        assert result == 20654

    def test_string_path(self):
        result = zst_compressed_mod_67_times_550_plus_decompressed_times_25_plus_file_size_times_32(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_67_times_550_plus_decompressed_times_25_plus_file_size_times_32(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes12PlusDecompressedMod130Times105PlusFileSizeTimes26:
    def test_returns_int(self):
        result = zst_compressed_times_12_plus_decompressed_mod_130_times_105_plus_file_size_times_26(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_12_plus_decompressed_mod_130_times_105_plus_file_size_times_26(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_12_plus_decompressed_mod_130_times_105_plus_file_size_times_26(_ZST)
        assert result == 10336

    def test_string_path(self):
        result = zst_compressed_times_12_plus_decompressed_mod_130_times_105_plus_file_size_times_26(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_12_plus_decompressed_mod_130_times_105_plus_file_size_times_26(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
