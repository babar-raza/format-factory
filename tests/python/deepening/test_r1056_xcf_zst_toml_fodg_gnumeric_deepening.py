"""Sprint 503 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_439_times_4600_plus_decompressed_times_183_plus_file_size_times_190,
    zst_compressed_times_153_plus_decompressed_mod_930_times_820_plus_file_size_times_186,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1374250
FN2_EXPECTED = 412008


class TestZstCompressedMod439Times4600PlusDecompressedTimes183PlusFileSizeTimes190:
    def test_returns_int(self):
        result = zst_compressed_mod_439_times_4600_plus_decompressed_times_183_plus_file_size_times_190(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_439_times_4600_plus_decompressed_times_183_plus_file_size_times_190(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_439_times_4600_plus_decompressed_times_183_plus_file_size_times_190(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_439_times_4600_plus_decompressed_times_183_plus_file_size_times_190(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_439_times_4600_plus_decompressed_times_183_plus_file_size_times_190(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes153PlusDecompressedMod930Times820PlusFileSizeTimes186:
    def test_returns_int(self):
        result = zst_compressed_times_153_plus_decompressed_mod_930_times_820_plus_file_size_times_186(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_153_plus_decompressed_mod_930_times_820_plus_file_size_times_186(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_153_plus_decompressed_mod_930_times_820_plus_file_size_times_186(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_153_plus_decompressed_mod_930_times_820_plus_file_size_times_186(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_153_plus_decompressed_mod_930_times_820_plus_file_size_times_186(_SAMPLE)
        assert result == FN2_EXPECTED
