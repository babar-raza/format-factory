"""Sprint R849 — ZST compound analytics deepening tests (Sprint 296)."""
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
    zst_compressed_mod_101_times_900_plus_decompressed_times_39_plus_file_size_times_46,
    zst_compressed_times_19_plus_decompressed_mod_200_times_140_plus_file_size_times_40,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod101Times900PlusDecompressedTimes39PlusFileSizeTimes46:
    def test_returns_int(self):
        result = zst_compressed_mod_101_times_900_plus_decompressed_times_39_plus_file_size_times_46(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_101_times_900_plus_decompressed_times_39_plus_file_size_times_46(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_101_times_900_plus_decompressed_times_39_plus_file_size_times_46(_ZST)
        assert result == 90722

    def test_string_path(self):
        result = zst_compressed_mod_101_times_900_plus_decompressed_times_39_plus_file_size_times_46(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_101_times_900_plus_decompressed_times_39_plus_file_size_times_46(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes19PlusDecompressedMod200Times140PlusFileSizeTimes40:
    def test_returns_int(self):
        result = zst_compressed_times_19_plus_decompressed_mod_200_times_140_plus_file_size_times_40(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_19_plus_decompressed_mod_200_times_140_plus_file_size_times_40(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_19_plus_decompressed_mod_200_times_140_plus_file_size_times_40(_ZST)
        assert result == 42648

    def test_string_path(self):
        result = zst_compressed_times_19_plus_decompressed_mod_200_times_140_plus_file_size_times_40(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_19_plus_decompressed_mod_200_times_140_plus_file_size_times_40(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
