"""Sprint 401 — ZST deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

try:
    import zstandard  # noqa: F401
except ImportError:
    import pytest
    pytest.skip("zstandard not installed", allow_module_level=True)

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_compressed_mod_253_times_2800_plus_decompressed_times_115_plus_file_size_times_122,
    zst_compressed_times_85_plus_decompressed_mod_580_times_470_plus_file_size_times_116,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 131234
FN2_EXPECTED = 237972


class TestZstCompressedMod253Times2800PlusDecompressedTimes115PlusFileSizeTimes122:
    def test_returns_int(self):
        result = zst_compressed_mod_253_times_2800_plus_decompressed_times_115_plus_file_size_times_122(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_253_times_2800_plus_decompressed_times_115_plus_file_size_times_122(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_253_times_2800_plus_decompressed_times_115_plus_file_size_times_122(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_253_times_2800_plus_decompressed_times_115_plus_file_size_times_122(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_253_times_2800_plus_decompressed_times_115_plus_file_size_times_122(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes85PlusDecompressedMod580Times470PlusFileSizeTimes116:
    def test_returns_int(self):
        result = zst_compressed_times_85_plus_decompressed_mod_580_times_470_plus_file_size_times_116(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_85_plus_decompressed_mod_580_times_470_plus_file_size_times_116(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_85_plus_decompressed_mod_580_times_470_plus_file_size_times_116(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_85_plus_decompressed_mod_580_times_470_plus_file_size_times_116(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_85_plus_decompressed_mod_580_times_470_plus_file_size_times_116(_SAMPLE)
        assert result == FN2_EXPECTED
