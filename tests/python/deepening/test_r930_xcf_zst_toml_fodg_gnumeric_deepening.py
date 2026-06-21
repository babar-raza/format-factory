"""Sprint 377 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_221_times_2350_plus_decompressed_times_97_plus_file_size_times_104,
    zst_compressed_times_67_plus_decompressed_mod_490_times_380_plus_file_size_times_98,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 185968
FN2_EXPECTED = 193080


class TestZstCompressedMod221Times2350PlusDecompressedTimes97PlusFileSizeTimes104:
    def test_returns_int(self):
        result = zst_compressed_mod_221_times_2350_plus_decompressed_times_97_plus_file_size_times_104(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_221_times_2350_plus_decompressed_times_97_plus_file_size_times_104(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_221_times_2350_plus_decompressed_times_97_plus_file_size_times_104(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_221_times_2350_plus_decompressed_times_97_plus_file_size_times_104(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_221_times_2350_plus_decompressed_times_97_plus_file_size_times_104(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes67PlusDecompressedMod490Times380PlusFileSizeTimes98:
    def test_returns_int(self):
        result = zst_compressed_times_67_plus_decompressed_mod_490_times_380_plus_file_size_times_98(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_67_plus_decompressed_mod_490_times_380_plus_file_size_times_98(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_67_plus_decompressed_mod_490_times_380_plus_file_size_times_98(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_67_plus_decompressed_mod_490_times_380_plus_file_size_times_98(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_67_plus_decompressed_mod_490_times_380_plus_file_size_times_98(_SAMPLE)
        assert result == FN2_EXPECTED
