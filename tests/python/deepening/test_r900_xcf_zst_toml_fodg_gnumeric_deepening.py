"""Sprint R900 — ZST compound analytics deepening tests (Sprint 347)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

try:
    import zstandard  # noqa: F401
except ImportError:
    pytest.skip("zstandard not installed", allow_module_level=True)

from src.python.zst import (
    zst_compressed_mod_197_times_1850_plus_decompressed_times_77_plus_file_size_times_84,
    zst_compressed_times_47_plus_decompressed_mod_390_times_280_plus_file_size_times_78,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod197Times1850PlusDecompressedTimes77PlusFileSizeTimes84:
    def test_returns_int(self):
        result = zst_compressed_mod_197_times_1850_plus_decompressed_times_77_plus_file_size_times_84(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_197_times_1850_plus_decompressed_times_77_plus_file_size_times_84(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_197_times_1850_plus_decompressed_times_77_plus_file_size_times_84(_ZST)
        assert result == 191628

    def test_string_path(self):
        result = zst_compressed_mod_197_times_1850_plus_decompressed_times_77_plus_file_size_times_84(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_197_times_1850_plus_decompressed_times_77_plus_file_size_times_84(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes47PlusDecompressedMod390Times280PlusFileSizeTimes78:
    def test_returns_int(self):
        result = zst_compressed_times_47_plus_decompressed_mod_390_times_280_plus_file_size_times_78(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_47_plus_decompressed_mod_390_times_280_plus_file_size_times_78(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_47_plus_decompressed_mod_390_times_280_plus_file_size_times_78(_ZST)
        assert result == 34000

    def test_string_path(self):
        result = zst_compressed_times_47_plus_decompressed_mod_390_times_280_plus_file_size_times_78(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_47_plus_decompressed_mod_390_times_280_plus_file_size_times_78(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
