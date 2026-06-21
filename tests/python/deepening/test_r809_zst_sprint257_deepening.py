"""Sprint 257 ZST deepening tests."""
from pathlib import Path
import pytest
import sys

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))
zstandard = pytest.importorskip("zstandard")

from src.python.zst import (
    zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220,
    zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400,
)

SAMPLES = _REPO / "samples/by-format/zst/valid"
BLOCK128K = SAMPLES / "block-128k.zst"
DICT_COMP = SAMPLES / "dict-compressed.zst"
EMPTY_BLK = SAMPLES / "empty-block.zst"


class TestZstMod229F1:
    def test_block128k_returns_int(self):
        assert isinstance(zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220(BLOCK128K), int)
    def test_block128k_expected_value(self):
        assert zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220(BLOCK128K) == 3298
    def test_dict_expected_value(self):
        assert zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220(DICT_COMP) == 28440
    def test_empty_expected_value(self):
        assert zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220(EMPTY_BLK) == 110
    def test_returns_nonnegative(self):
        assert zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220(EMPTY_BLK) >= 0
    def test_accepts_path_object(self):
        assert isinstance(zst_file_size_mod_229_times_10_plus_decompressed_size_mod_3300_plus_max_byte_value_times_220(Path(BLOCK128K)), int)


class TestZstTimes16F2:
    def test_block128k_returns_int(self):
        assert isinstance(zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400(BLOCK128K), int)
    def test_block128k_expected_value(self):
        assert zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400(BLOCK128K) == 2097564
    def test_dict_expected_value(self):
        assert zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400(DICT_COMP) == 25744
    def test_empty_expected_value(self):
        assert zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400(EMPTY_BLK) == 176
    def test_returns_nonnegative(self):
        assert zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400(EMPTY_BLK) >= 0
    def test_accepts_path_object(self):
        assert isinstance(zst_compressed_size_times_16_plus_decompressed_size_mod_600_plus_min_byte_value_times_2400(Path(BLOCK128K)), int)
