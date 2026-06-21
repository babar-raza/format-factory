"""Sprint 410 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_263_times_2950_plus_decompressed_times_121_plus_file_size_times_128,
    zst_compressed_times_91_plus_decompressed_mod_610_times_500_plus_file_size_times_122,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 108556
FN2_EXPECTED = 252936


class TestZstCompressedMod263Times2950PlusDecompressedTimes121PlusFileSizeTimes128:
    def test_returns_int(self):
        result = zst_compressed_mod_263_times_2950_plus_decompressed_times_121_plus_file_size_times_128(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_263_times_2950_plus_decompressed_times_121_plus_file_size_times_128(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_263_times_2950_plus_decompressed_times_121_plus_file_size_times_128(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_263_times_2950_plus_decompressed_times_121_plus_file_size_times_128(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_263_times_2950_plus_decompressed_times_121_plus_file_size_times_128(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes91PlusDecompressedMod610Times500PlusFileSizeTimes122:
    def test_returns_int(self):
        result = zst_compressed_times_91_plus_decompressed_mod_610_times_500_plus_file_size_times_122(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_91_plus_decompressed_mod_610_times_500_plus_file_size_times_122(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_91_plus_decompressed_mod_610_times_500_plus_file_size_times_122(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_91_plus_decompressed_mod_610_times_500_plus_file_size_times_122(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_91_plus_decompressed_mod_610_times_500_plus_file_size_times_122(_SAMPLE)
        assert result == FN2_EXPECTED
