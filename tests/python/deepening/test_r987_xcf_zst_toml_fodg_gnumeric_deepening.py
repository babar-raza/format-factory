"""Sprint 434 — ZST deepening: 2 compound analytics functions, 10 tests."""
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
    zst_compressed_mod_293_times_3350_plus_decompressed_times_137_plus_file_size_times_144,
    zst_compressed_times_107_plus_decompressed_mod_690_times_580_plus_file_size_times_138,
)

_SAMPLE = _REPO / "samples/by-format/zst/valid/text-compressed.zst"

FN1_EXPECTED = 1003798
FN2_EXPECTED = 292840


class TestZstCompressedMod293Times3350PlusDecompressedTimes137PlusFileSizeTimes144:
    def test_returns_int(self):
        result = zst_compressed_mod_293_times_3350_plus_decompressed_times_137_plus_file_size_times_144(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_mod_293_times_3350_plus_decompressed_times_137_plus_file_size_times_144(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = zst_compressed_mod_293_times_3350_plus_decompressed_times_137_plus_file_size_times_144(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_mod_293_times_3350_plus_decompressed_times_137_plus_file_size_times_144(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_mod_293_times_3350_plus_decompressed_times_137_plus_file_size_times_144(_SAMPLE)
        assert result == FN1_EXPECTED


class TestZstCompressedTimes107PlusDecompressedMod690Times580PlusFileSizeTimes138:
    def test_returns_int(self):
        result = zst_compressed_times_107_plus_decompressed_mod_690_times_580_plus_file_size_times_138(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = zst_compressed_times_107_plus_decompressed_mod_690_times_580_plus_file_size_times_138(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = zst_compressed_times_107_plus_decompressed_mod_690_times_580_plus_file_size_times_138(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = zst_compressed_times_107_plus_decompressed_mod_690_times_580_plus_file_size_times_138(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = zst_compressed_times_107_plus_decompressed_mod_690_times_580_plus_file_size_times_138(_SAMPLE)
        assert result == FN2_EXPECTED
