"""Sprint 404 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_257_times_2850_plus_decompressed_times_117_plus_file_size_times_124,
    zst_compressed_times_87_plus_decompressed_mod_590_times_480_plus_file_size_times_118,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 122108
FN2_EXPECTED = 242960


class TestZstCompressedMod257Times2850PlusDecompressedTimes117PlusFileSizeTimes124:
    def test_returns_int(self):
        result = zst_compressed_mod_257_times_2850_plus_decompressed_times_117_plus_file_size_times_124(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_257_times_2850_plus_decompressed_times_117_plus_file_size_times_124(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_257_times_2850_plus_decompressed_times_117_plus_file_size_times_124(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_257_times_2850_plus_decompressed_times_117_plus_file_size_times_124(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_257_times_2850_plus_decompressed_times_117_plus_file_size_times_124(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes87PlusDecompressedMod590Times480PlusFileSizeTimes118:
    def test_returns_int(self):
        result = zst_compressed_times_87_plus_decompressed_mod_590_times_480_plus_file_size_times_118(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_87_plus_decompressed_mod_590_times_480_plus_file_size_times_118(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_87_plus_decompressed_mod_590_times_480_plus_file_size_times_118(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_87_plus_decompressed_mod_590_times_480_plus_file_size_times_118(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_87_plus_decompressed_mod_590_times_480_plus_file_size_times_118(_SAMPLE)
        assert result == FN2_EXPECTED
