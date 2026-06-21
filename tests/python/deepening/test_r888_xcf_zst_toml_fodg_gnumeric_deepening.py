"""Sprint R888 — ZST compound analytics deepening tests (Sprint 335)."""
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
    zst_compressed_mod_179_times_1550_plus_decompressed_times_65_plus_file_size_times_72,
    zst_compressed_times_35_plus_decompressed_mod_330_times_220_plus_file_size_times_66,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod179Times1550PlusDecompressedTimes65PlusFileSizeTimes72:
    def test_returns_int(self):
        result = zst_compressed_mod_179_times_1550_plus_decompressed_times_65_plus_file_size_times_72(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_179_times_1550_plus_decompressed_times_65_plus_file_size_times_72(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_179_times_1550_plus_decompressed_times_65_plus_file_size_times_72(_ZST)
        assert result == 189084

    def test_string_path(self):
        result = zst_compressed_mod_179_times_1550_plus_decompressed_times_65_plus_file_size_times_72(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_179_times_1550_plus_decompressed_times_65_plus_file_size_times_72(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes35PlusDecompressedMod330Times220PlusFileSizeTimes66:
    def test_returns_int(self):
        result = zst_compressed_times_35_plus_decompressed_mod_330_times_220_plus_file_size_times_66(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_35_plus_decompressed_mod_330_times_220_plus_file_size_times_66(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_35_plus_decompressed_mod_330_times_220_plus_file_size_times_66(_ZST)
        assert result == 40672

    def test_string_path(self):
        result = zst_compressed_times_35_plus_decompressed_mod_330_times_220_plus_file_size_times_66(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_35_plus_decompressed_mod_330_times_220_plus_file_size_times_66(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
