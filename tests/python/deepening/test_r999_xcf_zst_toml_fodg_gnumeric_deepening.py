"""Sprint 446 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_311_times_3550_plus_decompressed_times_145_plus_file_size_times_152,
    zst_compressed_times_115_plus_decompressed_mod_730_times_620_plus_file_size_times_146,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1063494
FN2_EXPECTED = 312792


class TestZstCompressedMod311Times3550PlusDecompressedTimes145PlusFileSizeTimes152:
    def test_returns_int(self):
        result = zst_compressed_mod_311_times_3550_plus_decompressed_times_145_plus_file_size_times_152(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_311_times_3550_plus_decompressed_times_145_plus_file_size_times_152(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_311_times_3550_plus_decompressed_times_145_plus_file_size_times_152(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_311_times_3550_plus_decompressed_times_145_plus_file_size_times_152(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_311_times_3550_plus_decompressed_times_145_plus_file_size_times_152(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes115PlusDecompressedMod730Times620PlusFileSizeTimes146:
    def test_returns_int(self):
        result = zst_compressed_times_115_plus_decompressed_mod_730_times_620_plus_file_size_times_146(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_115_plus_decompressed_mod_730_times_620_plus_file_size_times_146(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_115_plus_decompressed_mod_730_times_620_plus_file_size_times_146(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_115_plus_decompressed_mod_730_times_620_plus_file_size_times_146(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_115_plus_decompressed_mod_730_times_620_plus_file_size_times_146(_SAMPLE)
        assert result == FN2_EXPECTED
