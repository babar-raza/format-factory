"""Sprint 491 - ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_409_times_4350_plus_decompressed_times_175_plus_file_size_times_182,
    zst_compressed_times_145_plus_decompressed_mod_890_times_780_plus_file_size_times_178,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1300954
FN2_EXPECTED = 392056


class TestZstCompressedMod409Times4350PlusDecompressedTimes175PlusFileSizeTimes182:
    def test_returns_int(self):
        result = zst_compressed_mod_409_times_4350_plus_decompressed_times_175_plus_file_size_times_182(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_409_times_4350_plus_decompressed_times_175_plus_file_size_times_182(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_409_times_4350_plus_decompressed_times_175_plus_file_size_times_182(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_409_times_4350_plus_decompressed_times_175_plus_file_size_times_182(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_409_times_4350_plus_decompressed_times_175_plus_file_size_times_182(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes145PlusDecompressedMod890Times780PlusFileSizeTimes178:
    def test_returns_int(self):
        result = zst_compressed_times_145_plus_decompressed_mod_890_times_780_plus_file_size_times_178(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_145_plus_decompressed_mod_890_times_780_plus_file_size_times_178(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_145_plus_decompressed_mod_890_times_780_plus_file_size_times_178(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_145_plus_decompressed_mod_890_times_780_plus_file_size_times_178(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_145_plus_decompressed_mod_890_times_780_plus_file_size_times_178(_SAMPLE)
        assert result == FN2_EXPECTED
