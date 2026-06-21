"""Sprint R831 — ZST compound analytics deepening tests (Sprint 278)."""
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
    zst_compressed_mod_71_times_600_plus_decompressed_times_27_plus_file_size_times_34,
    zst_compressed_times_13_plus_decompressed_mod_140_times_110_plus_file_size_times_28,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod71Times600PlusDecompressedTimes27PlusFileSizeTimes34:
    def test_returns_int(self):
        result = zst_compressed_mod_71_times_600_plus_decompressed_times_27_plus_file_size_times_34(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_71_times_600_plus_decompressed_times_27_plus_file_size_times_34(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_71_times_600_plus_decompressed_times_27_plus_file_size_times_34(_ZST)
        assert result == 55178

    def test_string_path(self):
        result = zst_compressed_mod_71_times_600_plus_decompressed_times_27_plus_file_size_times_34(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_71_times_600_plus_decompressed_times_27_plus_file_size_times_34(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes13PlusDecompressedMod140Times110PlusFileSizeTimes28:
    def test_returns_int(self):
        result = zst_compressed_times_13_plus_decompressed_mod_140_times_110_plus_file_size_times_28(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_13_plus_decompressed_mod_140_times_110_plus_file_size_times_28(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_13_plus_decompressed_mod_140_times_110_plus_file_size_times_28(_ZST)
        assert result == 23252

    def test_string_path(self):
        result = zst_compressed_times_13_plus_decompressed_mod_140_times_110_plus_file_size_times_28(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_13_plus_decompressed_mod_140_times_110_plus_file_size_times_28(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
