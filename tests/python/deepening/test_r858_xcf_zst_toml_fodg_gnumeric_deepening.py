"""Sprint R858 — ZST compound analytics deepening tests (Sprint 305)."""
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
    zst_compressed_mod_127_times_1050_plus_decompressed_times_45_plus_file_size_times_52,
    zst_compressed_times_23_plus_decompressed_mod_230_times_160_plus_file_size_times_46,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod127Times1050PlusDecompressedTimes45PlusFileSizeTimes52:
    def test_returns_int(self):
        result = zst_compressed_mod_127_times_1050_plus_decompressed_times_45_plus_file_size_times_52(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_127_times_1050_plus_decompressed_times_45_plus_file_size_times_52(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_127_times_1050_plus_decompressed_times_45_plus_file_size_times_52(_ZST)
        assert result == 50594

    def test_string_path(self):
        result = zst_compressed_mod_127_times_1050_plus_decompressed_times_45_plus_file_size_times_52(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_127_times_1050_plus_decompressed_times_45_plus_file_size_times_52(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes23PlusDecompressedMod230Times160PlusFileSizeTimes46:
    def test_returns_int(self):
        result = zst_compressed_times_23_plus_decompressed_mod_230_times_160_plus_file_size_times_46(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_23_plus_decompressed_mod_230_times_160_plus_file_size_times_46(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_23_plus_decompressed_mod_230_times_160_plus_file_size_times_46(_ZST)
        assert result == 44368

    def test_string_path(self):
        result = zst_compressed_times_23_plus_decompressed_mod_230_times_160_plus_file_size_times_46(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_23_plus_decompressed_mod_230_times_160_plus_file_size_times_46(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
