"""Sprint 416 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_271_times_3050_plus_decompressed_times_125_plus_file_size_times_132,
    zst_compressed_times_95_plus_decompressed_mod_630_times_520_plus_file_size_times_126,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 87704
FN2_EXPECTED = 262912


class TestZstCompressedMod271Times3050PlusDecompressedTimes125PlusFileSizeTimes132:
    def test_returns_int(self):
        result = zst_compressed_mod_271_times_3050_plus_decompressed_times_125_plus_file_size_times_132(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_271_times_3050_plus_decompressed_times_125_plus_file_size_times_132(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_271_times_3050_plus_decompressed_times_125_plus_file_size_times_132(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_271_times_3050_plus_decompressed_times_125_plus_file_size_times_132(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_271_times_3050_plus_decompressed_times_125_plus_file_size_times_132(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes95PlusDecompressedMod630Times520PlusFileSizeTimes126:
    def test_returns_int(self):
        result = zst_compressed_times_95_plus_decompressed_mod_630_times_520_plus_file_size_times_126(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_95_plus_decompressed_mod_630_times_520_plus_file_size_times_126(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_95_plus_decompressed_mod_630_times_520_plus_file_size_times_126(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_95_plus_decompressed_mod_630_times_520_plus_file_size_times_126(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_95_plus_decompressed_mod_630_times_520_plus_file_size_times_126(_SAMPLE)
        assert result == FN2_EXPECTED
