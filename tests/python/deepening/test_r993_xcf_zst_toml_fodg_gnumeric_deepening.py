"""Sprint 440 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_301_times_3450_plus_decompressed_times_141_plus_file_size_times_148,
    zst_compressed_times_111_plus_decompressed_mod_710_times_600_plus_file_size_times_142,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1033646
FN2_EXPECTED = 302816


class TestZstCompressedMod301Times3450PlusDecompressedTimes141PlusFileSizeTimes148:
    def test_returns_int(self):
        result = zst_compressed_mod_301_times_3450_plus_decompressed_times_141_plus_file_size_times_148(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_301_times_3450_plus_decompressed_times_141_plus_file_size_times_148(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_301_times_3450_plus_decompressed_times_141_plus_file_size_times_148(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_301_times_3450_plus_decompressed_times_141_plus_file_size_times_148(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_301_times_3450_plus_decompressed_times_141_plus_file_size_times_148(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes111PlusDecompressedMod710Times600PlusFileSizeTimes142:
    def test_returns_int(self):
        result = zst_compressed_times_111_plus_decompressed_mod_710_times_600_plus_file_size_times_142(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_111_plus_decompressed_mod_710_times_600_plus_file_size_times_142(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_111_plus_decompressed_mod_710_times_600_plus_file_size_times_142(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_111_plus_decompressed_mod_710_times_600_plus_file_size_times_142(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_111_plus_decompressed_mod_710_times_600_plus_file_size_times_142(_SAMPLE)
        assert result == FN2_EXPECTED
