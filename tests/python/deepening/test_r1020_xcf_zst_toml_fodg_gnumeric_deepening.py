"""Sprint 467 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_359_times_3900_plus_decompressed_times_159_plus_file_size_times_166,
    zst_compressed_times_129_plus_decompressed_mod_800_times_690_plus_file_size_times_160,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1167962
FN2_EXPECTED = 347708


class TestZstCompressedMod359Times3900PlusDecompressedTimes159PlusFileSizeTimes166:
    def test_returns_int(self):
        result = zst_compressed_mod_359_times_3900_plus_decompressed_times_159_plus_file_size_times_166(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_359_times_3900_plus_decompressed_times_159_plus_file_size_times_166(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_359_times_3900_plus_decompressed_times_159_plus_file_size_times_166(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_359_times_3900_plus_decompressed_times_159_plus_file_size_times_166(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_359_times_3900_plus_decompressed_times_159_plus_file_size_times_166(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes129PlusDecompressedMod800Times690PlusFileSizeTimes160:
    def test_returns_int(self):
        result = zst_compressed_times_129_plus_decompressed_mod_800_times_690_plus_file_size_times_160(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_129_plus_decompressed_mod_800_times_690_plus_file_size_times_160(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_129_plus_decompressed_mod_800_times_690_plus_file_size_times_160(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_129_plus_decompressed_mod_800_times_690_plus_file_size_times_160(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_129_plus_decompressed_mod_800_times_690_plus_file_size_times_160(_SAMPLE)
        assert result == FN2_EXPECTED
