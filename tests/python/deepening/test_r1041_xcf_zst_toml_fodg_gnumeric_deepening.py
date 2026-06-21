"""Sprint 488 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_397_times_4250_plus_decompressed_times_173_plus_file_size_times_180,
    zst_compressed_times_143_plus_decompressed_mod_880_times_770_plus_file_size_times_176,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1272430
FN2_EXPECTED = 387068


class TestZstCompressedMod397Times4250PlusDecompressedTimes173PlusFileSizeTimes180:
    def test_returns_int(self):
        result = zst_compressed_mod_397_times_4250_plus_decompressed_times_173_plus_file_size_times_180(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_397_times_4250_plus_decompressed_times_173_plus_file_size_times_180(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_397_times_4250_plus_decompressed_times_173_plus_file_size_times_180(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_397_times_4250_plus_decompressed_times_173_plus_file_size_times_180(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_397_times_4250_plus_decompressed_times_173_plus_file_size_times_180(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes143PlusDecompressedMod880Times770PlusFileSizeTimes176:
    def test_returns_int(self):
        result = zst_compressed_times_143_plus_decompressed_mod_880_times_770_plus_file_size_times_176(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_143_plus_decompressed_mod_880_times_770_plus_file_size_times_176(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_143_plus_decompressed_mod_880_times_770_plus_file_size_times_176(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_143_plus_decompressed_mod_880_times_770_plus_file_size_times_176(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_143_plus_decompressed_mod_880_times_770_plus_file_size_times_176(_SAMPLE)
        assert result == FN2_EXPECTED
