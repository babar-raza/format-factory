"""Sprint 425 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_283_times_3200_plus_decompressed_times_131_plus_file_size_times_138,
    zst_compressed_times_101_plus_decompressed_mod_660_times_550_plus_file_size_times_132,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 959026
FN2_EXPECTED = 277876


class TestZstCompressedMod283Times3200PlusDecompressedTimes131PlusFileSizeTimes138:
    def test_returns_int(self):
        result = zst_compressed_mod_283_times_3200_plus_decompressed_times_131_plus_file_size_times_138(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_283_times_3200_plus_decompressed_times_131_plus_file_size_times_138(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_283_times_3200_plus_decompressed_times_131_plus_file_size_times_138(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_283_times_3200_plus_decompressed_times_131_plus_file_size_times_138(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_283_times_3200_plus_decompressed_times_131_plus_file_size_times_138(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes101PlusDecompressedMod660Times550PlusFileSizeTimes132:
    def test_returns_int(self):
        result = zst_compressed_times_101_plus_decompressed_mod_660_times_550_plus_file_size_times_132(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_101_plus_decompressed_mod_660_times_550_plus_file_size_times_132(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_101_plus_decompressed_mod_660_times_550_plus_file_size_times_132(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_101_plus_decompressed_mod_660_times_550_plus_file_size_times_132(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_101_plus_decompressed_mod_660_times_550_plus_file_size_times_132(_SAMPLE)
        assert result == FN2_EXPECTED
