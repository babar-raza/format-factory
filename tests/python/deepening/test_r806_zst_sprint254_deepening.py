"""
Sprint 254 ZST deepening tests.
Functions: zst_file_size_mod_223_times_9_plus_decompressed_size_mod_3200_plus_max_byte_value_times_210
           zst_compressed_size_times_14_plus_decompressed_size_mod_500_plus_min_byte_value_times_2200
"""
from pathlib import Path
import pytest
import sys

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

zstandard = pytest.importorskip("zstandard")

from src.python.zst import (
    zst_file_size_mod_223_times_9_plus_decompressed_size_mod_3200_plus_max_byte_value_times_210,
    zst_compressed_size_times_14_plus_decompressed_size_mod_500_plus_min_byte_value_times_2200,
)

SAMPLES = _REPO / "samples/by-format/zst/valid"
BLOCK128K = SAMPLES / "block-128k.zst"
DICT_COMP = SAMPLES / "dict-compressed.zst"
EMPTY_BLK = SAMPLES / "empty-block.zst"


class TestZstMod223F1:
    def test_block128k_returns_int(self):
        assert isinstance(zst_file_size_mod_223_times_9_plus_decompressed_size_mod_3200_plus_max_byte_value_times_210(BLOCK128K), int)

    def test_block128k_expected_value(self):
        assert zst_file_size_mod_223_times_9_plus_decompressed_size_mod_3200_plus_max_byte_value_times_210(BLOCK128K) == 4688

    def test_dict_expected_value(self):
        assert zst_file_size_mod_223_times_9_plus_decompressed_size_mod_3200_plus_max_byte_value_times_210(DICT_COMP) == 27246

    def test_empty_expected_value(self):
        assert zst_file_size_mod_223_times_9_plus_decompressed_size_mod_3200_plus_max_byte_value_times_210(EMPTY_BLK) == 99

    def test_returns_nonnegative(self):
        assert zst_file_size_mod_223_times_9_plus_decompressed_size_mod_3200_plus_max_byte_value_times_210(EMPTY_BLK) >= 0

    def test_accepts_path_object(self):
        result = zst_file_size_mod_223_times_9_plus_decompressed_size_mod_3200_plus_max_byte_value_times_210(Path(BLOCK128K))
        assert isinstance(result, int)


class TestZstTimes14F2:
    def test_block128k_returns_int(self):
        assert isinstance(zst_compressed_size_times_14_plus_decompressed_size_mod_500_plus_min_byte_value_times_2200(BLOCK128K), int)

    def test_block128k_expected_value(self):
        assert zst_compressed_size_times_14_plus_decompressed_size_mod_500_plus_min_byte_value_times_2200(BLOCK128K) == 1835202

    def test_dict_expected_value(self):
        assert zst_compressed_size_times_14_plus_decompressed_size_mod_500_plus_min_byte_value_times_2200(DICT_COMP) == 23196

    def test_empty_expected_value(self):
        assert zst_compressed_size_times_14_plus_decompressed_size_mod_500_plus_min_byte_value_times_2200(EMPTY_BLK) == 154

    def test_returns_nonnegative(self):
        assert zst_compressed_size_times_14_plus_decompressed_size_mod_500_plus_min_byte_value_times_2200(EMPTY_BLK) >= 0

    def test_accepts_path_object(self):
        result = zst_compressed_size_times_14_plus_decompressed_size_mod_500_plus_min_byte_value_times_2200(Path(BLOCK128K))
        assert isinstance(result, int)
