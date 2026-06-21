"""Sprint R846 — ZST compound analytics deepening tests (Sprint 293)."""
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
    zst_compressed_mod_97_times_850_plus_decompressed_times_37_plus_file_size_times_44,
    zst_compressed_times_18_plus_decompressed_mod_190_times_135_plus_file_size_times_38,
)

SAMPLES = _REPO / "samples" / "by-format"
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")


class TestZstCompressedMod97Times850PlusDecompressedTimes37PlusFileSizeTimes44:
    def test_returns_int(self):
        result = zst_compressed_mod_97_times_850_plus_decompressed_times_37_plus_file_size_times_44(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_mod_97_times_850_plus_decompressed_times_37_plus_file_size_times_44(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_mod_97_times_850_plus_decompressed_times_37_plus_file_size_times_44(_ZST)
        assert result == 92698

    def test_string_path(self):
        result = zst_compressed_mod_97_times_850_plus_decompressed_times_37_plus_file_size_times_44(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_mod_97_times_850_plus_decompressed_times_37_plus_file_size_times_44(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)


class TestZstCompressedTimes18PlusDecompressedMod190Times135PlusFileSizeTimes38:
    def test_returns_int(self):
        result = zst_compressed_times_18_plus_decompressed_mod_190_times_135_plus_file_size_times_38(_ZST)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = zst_compressed_times_18_plus_decompressed_mod_190_times_135_plus_file_size_times_38(_ZST)
        assert result >= 0

    def test_expected_value(self):
        result = zst_compressed_times_18_plus_decompressed_mod_190_times_135_plus_file_size_times_38(_ZST)
        assert result == 16582

    def test_string_path(self):
        result = zst_compressed_times_18_plus_decompressed_mod_190_times_135_plus_file_size_times_38(str(_ZST))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = zst_compressed_times_18_plus_decompressed_mod_190_times_135_plus_file_size_times_38(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(result, int)
