"""Sprint R873 — ZST compound analytics deepening tests (Sprint 320)."""
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
    zst_compressed_mod_157_times_1300_plus_decompressed_times_55_plus_file_size_times_62,
    zst_compressed_times_28_plus_decompressed_mod_280_times_185_plus_file_size_times_56,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod157Times1300PlusDecompressedTimes55PlusFileSizeTimes62:
    def test_returns_int(self):
        result = zst_compressed_mod_157_times_1300_plus_decompressed_times_55_plus_file_size_times_62(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_157_times_1300_plus_decompressed_times_55_plus_file_size_times_62(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_157_times_1300_plus_decompressed_times_55_plus_file_size_times_62(_ZST)
        assert result == 187814

    def test_string_path(self):
        result = zst_compressed_mod_157_times_1300_plus_decompressed_times_55_plus_file_size_times_62(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_157_times_1300_plus_decompressed_times_55_plus_file_size_times_62(
            SAMPLES / "zst" / "valid" / "text-compressed.zst"
        )
        assert isinstance(result, int)


class TestZstCompressedTimes28PlusDecompressedMod280Times185PlusFileSizeTimes56:
    def test_returns_int(self):
        result = zst_compressed_times_28_plus_decompressed_mod_280_times_185_plus_file_size_times_56(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_28_plus_decompressed_mod_280_times_185_plus_file_size_times_56(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_28_plus_decompressed_mod_280_times_185_plus_file_size_times_56(_ZST)
        assert result == 43198

    def test_string_path(self):
        result = zst_compressed_times_28_plus_decompressed_mod_280_times_185_plus_file_size_times_56(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_28_plus_decompressed_mod_280_times_185_plus_file_size_times_56(
            SAMPLES / "zst" / "valid" / "text-compressed.zst"
        )
        assert isinstance(result, int)
