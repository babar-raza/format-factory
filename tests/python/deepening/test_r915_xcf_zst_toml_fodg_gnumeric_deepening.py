"""Sprint 362 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_211_times_2100_plus_decompressed_times_87_plus_file_size_times_94,
    zst_compressed_times_57_plus_decompressed_mod_440_times_330_plus_file_size_times_88,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 187598
FN2_EXPECTED = 168140


class TestZstCompressedMod211Times2100PlusDecompressedTimes87PlusFileSizeTimes94:
    def test_returns_int(self):
        result = zst_compressed_mod_211_times_2100_plus_decompressed_times_87_plus_file_size_times_94(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_211_times_2100_plus_decompressed_times_87_plus_file_size_times_94(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_211_times_2100_plus_decompressed_times_87_plus_file_size_times_94(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_211_times_2100_plus_decompressed_times_87_plus_file_size_times_94(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_211_times_2100_plus_decompressed_times_87_plus_file_size_times_94(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes57PlusDecompressedMod440Times330PlusFileSizeTimes88:
    def test_returns_int(self):
        result = zst_compressed_times_57_plus_decompressed_mod_440_times_330_plus_file_size_times_88(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_57_plus_decompressed_mod_440_times_330_plus_file_size_times_88(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_57_plus_decompressed_mod_440_times_330_plus_file_size_times_88(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_57_plus_decompressed_mod_440_times_330_plus_file_size_times_88(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_57_plus_decompressed_mod_440_times_330_plus_file_size_times_88(_SAMPLE)
        assert result == FN2_EXPECTED
