"""Sprint 479 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_383_times_4100_plus_decompressed_times_167_plus_file_size_times_174,
    zst_compressed_times_137_plus_decompressed_mod_840_times_730_plus_file_size_times_168,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1227658
FN2_EXPECTED = 367660


class TestZstCompressedMod383Times4100PlusDecompressedTimes167PlusFileSizeTimes174:
    def test_returns_int(self):
        result = zst_compressed_mod_383_times_4100_plus_decompressed_times_167_plus_file_size_times_174(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_383_times_4100_plus_decompressed_times_167_plus_file_size_times_174(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_383_times_4100_plus_decompressed_times_167_plus_file_size_times_174(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_383_times_4100_plus_decompressed_times_167_plus_file_size_times_174(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_383_times_4100_plus_decompressed_times_167_plus_file_size_times_174(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes137PlusDecompressedMod840Times730PlusFileSizeTimes168:
    def test_returns_int(self):
        result = zst_compressed_times_137_plus_decompressed_mod_840_times_730_plus_file_size_times_168(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_137_plus_decompressed_mod_840_times_730_plus_file_size_times_168(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_137_plus_decompressed_mod_840_times_730_plus_file_size_times_168(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_137_plus_decompressed_mod_840_times_730_plus_file_size_times_168(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_137_plus_decompressed_mod_840_times_730_plus_file_size_times_168(_SAMPLE)
        assert result == FN2_EXPECTED
