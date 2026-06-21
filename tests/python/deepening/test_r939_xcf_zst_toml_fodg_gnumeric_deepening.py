"""Sprint 386 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_229_times_2500_plus_decompressed_times_103_plus_file_size_times_110,
    zst_compressed_times_73_plus_decompressed_mod_520_times_410_plus_file_size_times_104,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 177590
FN2_EXPECTED = 208044


class TestZstCompressedMod229Times2500PlusDecompressedTimes103PlusFileSizeTimes110:
    def test_returns_int(self):
        result = zst_compressed_mod_229_times_2500_plus_decompressed_times_103_plus_file_size_times_110(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_229_times_2500_plus_decompressed_times_103_plus_file_size_times_110(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_229_times_2500_plus_decompressed_times_103_plus_file_size_times_110(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_229_times_2500_plus_decompressed_times_103_plus_file_size_times_110(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_229_times_2500_plus_decompressed_times_103_plus_file_size_times_110(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes73PlusDecompressedMod520Times410PlusFileSizeTimes104:
    def test_returns_int(self):
        result = zst_compressed_times_73_plus_decompressed_mod_520_times_410_plus_file_size_times_104(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_73_plus_decompressed_mod_520_times_410_plus_file_size_times_104(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_73_plus_decompressed_mod_520_times_410_plus_file_size_times_104(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_73_plus_decompressed_mod_520_times_410_plus_file_size_times_104(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_73_plus_decompressed_mod_520_times_410_plus_file_size_times_104(_SAMPLE)
        assert result == FN2_EXPECTED
