"""Sprint 356 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_203_times_2000_plus_decompressed_times_83_plus_file_size_times_90,
    zst_compressed_times_53_plus_decompressed_mod_420_times_310_plus_file_size_times_84,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 194850
FN2_EXPECTED = 158164


class TestZstCompressedMod203Times2000PlusDecompressedTimes83PlusFileSizeTimes90:
    def test_returns_int(self):
        result = zst_compressed_mod_203_times_2000_plus_decompressed_times_83_plus_file_size_times_90(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_203_times_2000_plus_decompressed_times_83_plus_file_size_times_90(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_203_times_2000_plus_decompressed_times_83_plus_file_size_times_90(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_203_times_2000_plus_decompressed_times_83_plus_file_size_times_90(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_203_times_2000_plus_decompressed_times_83_plus_file_size_times_90(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes53PlusDecompressedMod420Times310PlusFileSizeTimes84:
    def test_returns_int(self):
        result = zst_compressed_times_53_plus_decompressed_mod_420_times_310_plus_file_size_times_84(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_53_plus_decompressed_mod_420_times_310_plus_file_size_times_84(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_53_plus_decompressed_mod_420_times_310_plus_file_size_times_84(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_53_plus_decompressed_mod_420_times_310_plus_file_size_times_84(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_53_plus_decompressed_mod_420_times_310_plus_file_size_times_84(_SAMPLE)
        assert result == FN2_EXPECTED
