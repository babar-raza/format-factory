"""Sprint R897 — ZST compound analytics deepening tests (Sprint 344)."""
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
    zst_compressed_mod_191_times_1750_plus_decompressed_times_73_plus_file_size_times_80,
    zst_compressed_times_43_plus_decompressed_mod_370_times_260_plus_file_size_times_74,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod191Times1750PlusDecompressedTimes73PlusFileSizeTimes80:
    def test_returns_int(self):
        result = zst_compressed_mod_191_times_1750_plus_decompressed_times_73_plus_file_size_times_80(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_191_times_1750_plus_decompressed_times_73_plus_file_size_times_80(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_191_times_1750_plus_decompressed_times_73_plus_file_size_times_80(_ZST)
        assert result == 191980

    def test_string_path(self):
        result = zst_compressed_mod_191_times_1750_plus_decompressed_times_73_plus_file_size_times_80(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_191_times_1750_plus_decompressed_times_73_plus_file_size_times_80(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes43PlusDecompressedMod370Times260PlusFileSizeTimes74:
    def test_returns_int(self):
        result = zst_compressed_times_43_plus_decompressed_mod_370_times_260_plus_file_size_times_74(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_43_plus_decompressed_mod_370_times_260_plus_file_size_times_74(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_43_plus_decompressed_mod_370_times_260_plus_file_size_times_74(_ZST)
        assert result == 37024

    def test_string_path(self):
        result = zst_compressed_times_43_plus_decompressed_mod_370_times_260_plus_file_size_times_74(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_43_plus_decompressed_mod_370_times_260_plus_file_size_times_74(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
