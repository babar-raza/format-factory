"""Sprint 437 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_297_times_3400_plus_decompressed_times_139_plus_file_size_times_146,
    zst_compressed_times_109_plus_decompressed_mod_700_times_590_plus_file_size_times_140,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1018722
FN2_EXPECTED = 297828


class TestZstCompressedMod297Times3400PlusDecompressedTimes139PlusFileSizeTimes146:
    def test_returns_int(self):
        result = zst_compressed_mod_297_times_3400_plus_decompressed_times_139_plus_file_size_times_146(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_297_times_3400_plus_decompressed_times_139_plus_file_size_times_146(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_297_times_3400_plus_decompressed_times_139_plus_file_size_times_146(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_297_times_3400_plus_decompressed_times_139_plus_file_size_times_146(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_297_times_3400_plus_decompressed_times_139_plus_file_size_times_146(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes109PlusDecompressedMod700Times590PlusFileSizeTimes140:
    def test_returns_int(self):
        result = zst_compressed_times_109_plus_decompressed_mod_700_times_590_plus_file_size_times_140(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_109_plus_decompressed_mod_700_times_590_plus_file_size_times_140(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_109_plus_decompressed_mod_700_times_590_plus_file_size_times_140(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_109_plus_decompressed_mod_700_times_590_plus_file_size_times_140(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_109_plus_decompressed_mod_700_times_590_plus_file_size_times_140(_SAMPLE)
        assert result == FN2_EXPECTED
