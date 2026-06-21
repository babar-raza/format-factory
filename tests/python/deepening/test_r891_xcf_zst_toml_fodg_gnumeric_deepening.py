"""Sprint R891 — ZST compound analytics deepening tests (Sprint 338)."""
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
    zst_compressed_mod_181_times_1600_plus_decompressed_times_67_plus_file_size_times_74,
    zst_compressed_times_37_plus_decompressed_mod_340_times_230_plus_file_size_times_68,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod181Times1600PlusDecompressedTimes67PlusFileSizeTimes74:
    def test_returns_int(self):
        result = zst_compressed_mod_181_times_1600_plus_decompressed_times_67_plus_file_size_times_74(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_181_times_1600_plus_decompressed_times_67_plus_file_size_times_74(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_181_times_1600_plus_decompressed_times_67_plus_file_size_times_74(_ZST)
        assert result == 191858

    def test_string_path(self):
        result = zst_compressed_mod_181_times_1600_plus_decompressed_times_67_plus_file_size_times_74(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_181_times_1600_plus_decompressed_times_67_plus_file_size_times_74(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes37PlusDecompressedMod340Times230PlusFileSizeTimes68:
    def test_returns_int(self):
        result = zst_compressed_times_37_plus_decompressed_mod_340_times_230_plus_file_size_times_68(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_37_plus_decompressed_mod_340_times_230_plus_file_size_times_68(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_37_plus_decompressed_mod_340_times_230_plus_file_size_times_68(_ZST)
        assert result == 40060

    def test_string_path(self):
        result = zst_compressed_times_37_plus_decompressed_mod_340_times_230_plus_file_size_times_68(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_37_plus_decompressed_mod_340_times_230_plus_file_size_times_68(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
