"""Sprint 518 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_463_times_4850_plus_decompressed_times_193_plus_file_size_times_200,
    zst_compressed_times_163_plus_decompressed_mod_980_times_870_plus_file_size_times_196,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1448870
FN2_EXPECTED = 436948


class TestZstCompressedMod463Times4850PlusDecompressedTimes193PlusFileSizeTimes200:
    def test_returns_int(self):
        result = zst_compressed_mod_463_times_4850_plus_decompressed_times_193_plus_file_size_times_200(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_463_times_4850_plus_decompressed_times_193_plus_file_size_times_200(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_463_times_4850_plus_decompressed_times_193_plus_file_size_times_200(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_463_times_4850_plus_decompressed_times_193_plus_file_size_times_200(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_463_times_4850_plus_decompressed_times_193_plus_file_size_times_200(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes163PlusDecompressedMod980Times870PlusFileSizeTimes196:
    def test_returns_int(self):
        result = zst_compressed_times_163_plus_decompressed_mod_980_times_870_plus_file_size_times_196(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_163_plus_decompressed_mod_980_times_870_plus_file_size_times_196(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_163_plus_decompressed_mod_980_times_870_plus_file_size_times_196(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_163_plus_decompressed_mod_980_times_870_plus_file_size_times_196(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_163_plus_decompressed_mod_980_times_870_plus_file_size_times_196(_SAMPLE)
        assert result == FN2_EXPECTED
