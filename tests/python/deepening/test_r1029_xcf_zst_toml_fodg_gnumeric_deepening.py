"""Sprint 476 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_379_times_4050_plus_decompressed_times_165_plus_file_size_times_172,
    zst_compressed_times_135_plus_decompressed_mod_830_times_720_plus_file_size_times_166,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1212734
FN2_EXPECTED = 362672


class TestZstCompressedMod379Times4050PlusDecompressedTimes165PlusFileSizeTimes172:
    def test_returns_int(self):
        result = zst_compressed_mod_379_times_4050_plus_decompressed_times_165_plus_file_size_times_172(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_379_times_4050_plus_decompressed_times_165_plus_file_size_times_172(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_379_times_4050_plus_decompressed_times_165_plus_file_size_times_172(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_379_times_4050_plus_decompressed_times_165_plus_file_size_times_172(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_379_times_4050_plus_decompressed_times_165_plus_file_size_times_172(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes135PlusDecompressedMod830Times720PlusFileSizeTimes166:
    def test_returns_int(self):
        result = zst_compressed_times_135_plus_decompressed_mod_830_times_720_plus_file_size_times_166(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_135_plus_decompressed_mod_830_times_720_plus_file_size_times_166(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_135_plus_decompressed_mod_830_times_720_plus_file_size_times_166(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_135_plus_decompressed_mod_830_times_720_plus_file_size_times_166(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_135_plus_decompressed_mod_830_times_720_plus_file_size_times_166(_SAMPLE)
        assert result == FN2_EXPECTED
