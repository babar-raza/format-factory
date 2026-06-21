"""Sprint R879 — ZST compound analytics deepening tests (Sprint 326)."""
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
    zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
    zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedSizeMod293Times19PlusDecompressedSizeMod1000Times3PlusMaxByteValueTimes100:
    def test_returns_int(self):
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_ZST)
        assert result == 18438

    def test_string_path(self):
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(
            SAMPLES / "zst" / "valid" / "text-compressed.zst"
        )
        assert isinstance(result, int)


class TestZstCompressedSizeTimes29PlusDecompressedSizeTimes3PlusMaxByteValueTimes7:
    def test_returns_int(self):
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_ZST)
        assert result == 9905

    def test_string_path(self):
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(
            SAMPLES / "zst" / "valid" / "text-compressed.zst"
        )
        assert isinstance(result, int)
