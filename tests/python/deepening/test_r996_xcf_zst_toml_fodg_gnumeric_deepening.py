"""Sprint 443 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_307_times_3500_plus_decompressed_times_143_plus_file_size_times_150,
    zst_compressed_times_113_plus_decompressed_mod_720_times_610_plus_file_size_times_144,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1048570
FN2_EXPECTED = 307804


class TestZstCompressedMod307Times3500PlusDecompressedTimes143PlusFileSizeTimes150:
    def test_returns_int(self):
        result = zst_compressed_mod_307_times_3500_plus_decompressed_times_143_plus_file_size_times_150(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_307_times_3500_plus_decompressed_times_143_plus_file_size_times_150(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_307_times_3500_plus_decompressed_times_143_plus_file_size_times_150(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_307_times_3500_plus_decompressed_times_143_plus_file_size_times_150(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_307_times_3500_plus_decompressed_times_143_plus_file_size_times_150(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes113PlusDecompressedMod720Times610PlusFileSizeTimes144:
    def test_returns_int(self):
        result = zst_compressed_times_113_plus_decompressed_mod_720_times_610_plus_file_size_times_144(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_113_plus_decompressed_mod_720_times_610_plus_file_size_times_144(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_113_plus_decompressed_mod_720_times_610_plus_file_size_times_144(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_113_plus_decompressed_mod_720_times_610_plus_file_size_times_144(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_113_plus_decompressed_mod_720_times_610_plus_file_size_times_144(_SAMPLE)
        assert result == FN2_EXPECTED
