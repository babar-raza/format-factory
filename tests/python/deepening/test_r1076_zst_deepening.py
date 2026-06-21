"""Sprint 523 - ZST deepening: 2 compound analytics functions, 20 tests.

skill_id: /add-analytics-function
format_id: zst
target: src/python/zst/zst_analytics.py
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.zst import (
    zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204,
    zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200,
)

_SAMPLE_TEXT = _REPO / "samples/by-format/zst/valid/text-compressed.zst"
_SAMPLE_MINIMAL = _REPO / "samples/by-format/zst/valid/minimal-synthetic.zst"
_SAMPLE_RANDOM = _REPO / "samples/by-format/zst/valid/random-data.zst"

FN1_TEXT = 1478718
FN1_MINIMAL = 51737
FN1_RANDOM = 1624232

FN2_TEXT = 446924
FN2_MINIMAL = 4560
FN2_RANDOM = 122652


class TestZstCompressedMod479Times4950PlusDecompressedTimes197PlusFileSizeTimes204:
    def test_returns_int_text(self):
        assert isinstance(
            zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_TEXT),
            int,
        )

    def test_returns_int_minimal(self):
        assert isinstance(
            zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_MINIMAL),
            int,
        )

    def test_returns_int_random(self):
        assert isinstance(
            zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_RANDOM),
            int,
        )

    def test_expected_text(self):
        assert zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_TEXT) == FN1_TEXT

    def test_expected_minimal(self):
        assert zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_MINIMAL) == FN1_MINIMAL

    def test_expected_random(self):
        assert zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_RANDOM) == FN1_RANDOM

    def test_positive_result_text(self):
        assert zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_TEXT) > 0

    def test_positive_result_minimal(self):
        assert zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_MINIMAL) > 0

    def test_text_differs_from_minimal(self):
        r1 = zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_TEXT)
        r2 = zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_MINIMAL)
        assert r1 != r2

    def test_random_differs_from_text(self):
        r1 = zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_RANDOM)
        r2 = zst_compressed_mod_479_times_4950_plus_decompressed_times_197_plus_file_size_times_204(_SAMPLE_TEXT)
        assert r1 != r2


class TestZstCompressedTimes167PlusDecompressedMod1000Times890PlusFileSizeTimes200:
    def test_returns_int_text(self):
        assert isinstance(
            zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_TEXT),
            int,
        )

    def test_returns_int_minimal(self):
        assert isinstance(
            zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_MINIMAL),
            int,
        )

    def test_returns_int_random(self):
        assert isinstance(
            zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_RANDOM),
            int,
        )

    def test_expected_text(self):
        assert zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_TEXT) == FN2_TEXT

    def test_expected_minimal(self):
        assert zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_MINIMAL) == FN2_MINIMAL

    def test_expected_random(self):
        assert zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_RANDOM) == FN2_RANDOM

    def test_positive_result_text(self):
        assert zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_TEXT) > 0

    def test_positive_result_minimal(self):
        assert zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_MINIMAL) > 0

    def test_text_differs_from_minimal(self):
        r1 = zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_TEXT)
        r2 = zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_MINIMAL)
        assert r1 != r2

    def test_random_differs_from_text(self):
        r1 = zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_RANDOM)
        r2 = zst_compressed_times_167_plus_decompressed_mod_1000_times_890_plus_file_size_times_200(_SAMPLE_TEXT)
        assert r1 != r2
