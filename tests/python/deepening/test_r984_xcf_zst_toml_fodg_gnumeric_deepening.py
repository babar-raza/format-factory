"""Sprint 431 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_289_times_3300_plus_decompressed_times_135_plus_file_size_times_142,
    zst_compressed_times_105_plus_decompressed_mod_680_times_570_plus_file_size_times_136,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 988874
FN2_EXPECTED = 287852


class TestZstCompressedMod289Times3300PlusDecompressedTimes135PlusFileSizeTimes142:
    def test_returns_int(self):
        result = zst_compressed_mod_289_times_3300_plus_decompressed_times_135_plus_file_size_times_142(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_289_times_3300_plus_decompressed_times_135_plus_file_size_times_142(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_289_times_3300_plus_decompressed_times_135_plus_file_size_times_142(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_289_times_3300_plus_decompressed_times_135_plus_file_size_times_142(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_289_times_3300_plus_decompressed_times_135_plus_file_size_times_142(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes105PlusDecompressedMod680Times570PlusFileSizeTimes136:
    def test_returns_int(self):
        result = zst_compressed_times_105_plus_decompressed_mod_680_times_570_plus_file_size_times_136(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_105_plus_decompressed_mod_680_times_570_plus_file_size_times_136(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_105_plus_decompressed_mod_680_times_570_plus_file_size_times_136(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_105_plus_decompressed_mod_680_times_570_plus_file_size_times_136(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_105_plus_decompressed_mod_680_times_570_plus_file_size_times_136(_SAMPLE)
        assert result == FN2_EXPECTED
