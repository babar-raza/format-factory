"""Sprint R870 — ZST compound analytics deepening tests (Sprint 317)."""
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
    zst_compressed_mod_151_times_1250_plus_decompressed_times_53_plus_file_size_times_60,
    zst_compressed_times_27_plus_decompressed_mod_270_times_180_plus_file_size_times_54,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod151Times1250PlusDecompressedTimes53PlusFileSizeTimes60:
    def test_returns_int(self):
        result = zst_compressed_mod_151_times_1250_plus_decompressed_times_53_plus_file_size_times_60(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_151_times_1250_plus_decompressed_times_53_plus_file_size_times_60(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_151_times_1250_plus_decompressed_times_53_plus_file_size_times_60(_ZST)
        assert result == 188240

    def test_string_path(self):
        result = zst_compressed_mod_151_times_1250_plus_decompressed_times_53_plus_file_size_times_60(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_151_times_1250_plus_decompressed_times_53_plus_file_size_times_60(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes27PlusDecompressedMod270Times180PlusFileSizeTimes54:
    def test_returns_int(self):
        result = zst_compressed_times_27_plus_decompressed_mod_270_times_180_plus_file_size_times_54(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_27_plus_decompressed_mod_270_times_180_plus_file_size_times_54(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_27_plus_decompressed_mod_270_times_180_plus_file_size_times_54(_ZST)
        assert result == 43632

    def test_string_path(self):
        result = zst_compressed_times_27_plus_decompressed_mod_270_times_180_plus_file_size_times_54(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_27_plus_decompressed_mod_270_times_180_plus_file_size_times_54(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
