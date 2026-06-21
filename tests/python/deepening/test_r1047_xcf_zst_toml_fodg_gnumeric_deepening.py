"""Sprint 494 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_419_times_4400_plus_decompressed_times_177_plus_file_size_times_184,
    zst_compressed_times_147_plus_decompressed_mod_900_times_790_plus_file_size_times_180,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1315878
FN2_EXPECTED = 397044


class TestZstCompressedMod419Times4400PlusDecompressedTimes177PlusFileSizeTimes184:
    def test_returns_int(self):
        result = zst_compressed_mod_419_times_4400_plus_decompressed_times_177_plus_file_size_times_184(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_419_times_4400_plus_decompressed_times_177_plus_file_size_times_184(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_419_times_4400_plus_decompressed_times_177_plus_file_size_times_184(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_419_times_4400_plus_decompressed_times_177_plus_file_size_times_184(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_419_times_4400_plus_decompressed_times_177_plus_file_size_times_184(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes147PlusDecompressedMod900Times790PlusFileSizeTimes180:
    def test_returns_int(self):
        result = zst_compressed_times_147_plus_decompressed_mod_900_times_790_plus_file_size_times_180(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_147_plus_decompressed_mod_900_times_790_plus_file_size_times_180(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_147_plus_decompressed_mod_900_times_790_plus_file_size_times_180(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_147_plus_decompressed_mod_900_times_790_plus_file_size_times_180(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_147_plus_decompressed_mod_900_times_790_plus_file_size_times_180(_SAMPLE)
        assert result == FN2_EXPECTED
