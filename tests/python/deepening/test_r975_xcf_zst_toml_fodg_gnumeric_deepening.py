"""Sprint 422 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_281_times_3150_plus_decompressed_times_129_plus_file_size_times_136,
    zst_compressed_times_99_plus_decompressed_mod_650_times_540_plus_file_size_times_130,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 944102
FN2_EXPECTED = 272888


class TestZstCompressedMod281Times3150PlusDecompressedTimes129PlusFileSizeTimes136:
    def test_returns_int(self):
        result = zst_compressed_mod_281_times_3150_plus_decompressed_times_129_plus_file_size_times_136(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_281_times_3150_plus_decompressed_times_129_plus_file_size_times_136(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_281_times_3150_plus_decompressed_times_129_plus_file_size_times_136(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_281_times_3150_plus_decompressed_times_129_plus_file_size_times_136(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_281_times_3150_plus_decompressed_times_129_plus_file_size_times_136(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes99PlusDecompressedMod650Times540PlusFileSizeTimes130:
    def test_returns_int(self):
        result = zst_compressed_times_99_plus_decompressed_mod_650_times_540_plus_file_size_times_130(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_99_plus_decompressed_mod_650_times_540_plus_file_size_times_130(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_99_plus_decompressed_mod_650_times_540_plus_file_size_times_130(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_99_plus_decompressed_mod_650_times_540_plus_file_size_times_130(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_99_plus_decompressed_mod_650_times_540_plus_file_size_times_130(_SAMPLE)
        assert result == FN2_EXPECTED
