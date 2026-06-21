"""Sprint 512 - ZST deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

try:
    import zstandard  # noqa: F401
except ImportError:
    pytest.skip("zstandard not installed", allow_module_level=True)

from src.python.zst import (
    zst_compressed_mod_457_times_4750_plus_decompressed_times_189_plus_file_size_times_196,
    zst_compressed_times_159_plus_decompressed_mod_960_times_850_plus_file_size_times_192,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1419022
FN2_EXPECTED = 426972


class TestZstCompressedMod457Times4750PlusDecompressedTimes189PlusFileSizeTimes196:
    def test_returns_int(self):
        result = zst_compressed_mod_457_times_4750_plus_decompressed_times_189_plus_file_size_times_196(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_457_times_4750_plus_decompressed_times_189_plus_file_size_times_196(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_457_times_4750_plus_decompressed_times_189_plus_file_size_times_196(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_457_times_4750_plus_decompressed_times_189_plus_file_size_times_196(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_457_times_4750_plus_decompressed_times_189_plus_file_size_times_196(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes159PlusDecompressedMod960Times850PlusFileSizeTimes192:
    def test_returns_int(self):
        result = zst_compressed_times_159_plus_decompressed_mod_960_times_850_plus_file_size_times_192(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_159_plus_decompressed_mod_960_times_850_plus_file_size_times_192(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_159_plus_decompressed_mod_960_times_850_plus_file_size_times_192(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_159_plus_decompressed_mod_960_times_850_plus_file_size_times_192(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_159_plus_decompressed_mod_960_times_850_plus_file_size_times_192(_SAMPLE)
        assert result == FN2_EXPECTED
