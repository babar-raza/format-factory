"""Sprint 419 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_277_times_3100_plus_decompressed_times_127_plus_file_size_times_134,
    zst_compressed_times_97_plus_decompressed_mod_640_times_530_plus_file_size_times_128,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 929178
FN2_EXPECTED = 267900


class TestZstCompressedMod277Times3100PlusDecompressedTimes127PlusFileSizeTimes134:
    def test_returns_int(self):
        result = zst_compressed_mod_277_times_3100_plus_decompressed_times_127_plus_file_size_times_134(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_277_times_3100_plus_decompressed_times_127_plus_file_size_times_134(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_277_times_3100_plus_decompressed_times_127_plus_file_size_times_134(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_277_times_3100_plus_decompressed_times_127_plus_file_size_times_134(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_277_times_3100_plus_decompressed_times_127_plus_file_size_times_134(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes97PlusDecompressedMod640Times530PlusFileSizeTimes128:
    def test_returns_int(self):
        result = zst_compressed_times_97_plus_decompressed_mod_640_times_530_plus_file_size_times_128(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_97_plus_decompressed_mod_640_times_530_plus_file_size_times_128(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_97_plus_decompressed_mod_640_times_530_plus_file_size_times_128(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_97_plus_decompressed_mod_640_times_530_plus_file_size_times_128(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_97_plus_decompressed_mod_640_times_530_plus_file_size_times_128(_SAMPLE)
        assert result == FN2_EXPECTED
