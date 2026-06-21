"""
Sprint 251 ZST deepening tests.
Functions: zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200
           zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000
"""
from pathlib import Path
import pytest
import sys

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

zstandard = pytest.importorskip("zstandard")

from src.python.zst import (
    zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200,
    zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000,
)

SAMPLES = _REPO / "samples/by-format/zst/valid"
BLOCK128K = SAMPLES / "block-128k.zst"
DICT_COMP = SAMPLES / "dict-compressed.zst"
EMPTY_BLK = SAMPLES / "empty-block.zst"


class TestZstMod211F1:
    def test_block128k_returns_int(self):
        assert isinstance(zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200(BLOCK128K), int)

    def test_block128k_expected_value(self):
        assert zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200(BLOCK128K) == 1268

    def test_dict_expected_value(self):
        assert zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200(DICT_COMP) == 26052

    def test_empty_expected_value(self):
        assert zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200(EMPTY_BLK) == 88

    def test_returns_nonnegative(self):
        assert zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200(EMPTY_BLK) >= 0

    def test_accepts_path_object(self):
        result = zst_file_size_mod_211_times_8_plus_decompressed_size_mod_3100_plus_max_byte_value_times_200(Path(BLOCK128K))
        assert isinstance(result, int)


class TestZstTimes12F2:
    def test_block128k_returns_int(self):
        assert isinstance(zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000(BLOCK128K), int)

    def test_block128k_expected_value(self):
        assert zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000(BLOCK128K) == 1573240

    def test_dict_expected_value(self):
        assert zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000(DICT_COMP) == 21048

    def test_empty_expected_value(self):
        assert zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000(EMPTY_BLK) == 132

    def test_returns_nonnegative(self):
        assert zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000(EMPTY_BLK) >= 0

    def test_accepts_path_object(self):
        result = zst_compressed_size_times_12_plus_decompressed_size_mod_400_plus_min_byte_value_times_2000(Path(BLOCK128K))
        assert isinstance(result, int)
