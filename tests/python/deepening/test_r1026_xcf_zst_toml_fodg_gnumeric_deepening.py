"""Sprint 473 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_373_times_4000_plus_decompressed_times_163_plus_file_size_times_170,
    zst_compressed_times_133_plus_decompressed_mod_820_times_710_plus_file_size_times_164,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1197810
FN2_EXPECTED = 357684


class TestZstCompressedMod373Times4000PlusDecompressedTimes163PlusFileSizeTimes170:
    def test_returns_int(self):
        result = zst_compressed_mod_373_times_4000_plus_decompressed_times_163_plus_file_size_times_170(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_373_times_4000_plus_decompressed_times_163_plus_file_size_times_170(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_373_times_4000_plus_decompressed_times_163_plus_file_size_times_170(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_373_times_4000_plus_decompressed_times_163_plus_file_size_times_170(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_373_times_4000_plus_decompressed_times_163_plus_file_size_times_170(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes133PlusDecompressedMod820Times710PlusFileSizeTimes164:
    def test_returns_int(self):
        result = zst_compressed_times_133_plus_decompressed_mod_820_times_710_plus_file_size_times_164(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_133_plus_decompressed_mod_820_times_710_plus_file_size_times_164(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_133_plus_decompressed_mod_820_times_710_plus_file_size_times_164(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_133_plus_decompressed_mod_820_times_710_plus_file_size_times_164(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_133_plus_decompressed_mod_820_times_710_plus_file_size_times_164(_SAMPLE)
        assert result == FN2_EXPECTED
