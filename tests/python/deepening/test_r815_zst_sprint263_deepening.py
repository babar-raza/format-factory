"""Sprint 263 ZST deepening tests."""
from pathlib import Path
import pytest, sys
_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))
zstandard = pytest.importorskip("zstandard")
from src.python.zst import (
    zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240,
    zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800,
)
SAMPLES = _REPO / "samples/by-format/zst/valid"
BLOCK128K = SAMPLES / "block-128k.zst"; DICT_COMP = SAMPLES / "dict-compressed.zst"; EMPTY_BLK = SAMPLES / "empty-block.zst"

class TestZstMod241F1:
    def test_block128k_returns_int(self): assert isinstance(zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240(BLOCK128K), int)
    def test_block128k_expected_value(self): assert zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240(BLOCK128K) == 4184
    def test_dict_expected_value(self): assert zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240(DICT_COMP) == 30828
    def test_empty_expected_value(self): assert zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240(EMPTY_BLK) == 132
    def test_returns_nonnegative(self): assert zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240(EMPTY_BLK) >= 0
    def test_accepts_path_object(self): assert isinstance(zst_file_size_mod_241_times_12_plus_decompressed_size_mod_3500_plus_max_byte_value_times_240(Path(BLOCK128K)), int)

class TestZstTimes20F2:
    def test_block128k_returns_int(self): assert isinstance(zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800(BLOCK128K), int)
    def test_block128k_expected_value(self): assert zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800(BLOCK128K) == 2622288
    def test_dict_expected_value(self): assert zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800(DICT_COMP) == 29640
    def test_empty_expected_value(self): assert zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800(EMPTY_BLK) == 220
    def test_returns_nonnegative(self): assert zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800(EMPTY_BLK) >= 0
    def test_accepts_path_object(self): assert isinstance(zst_compressed_size_times_20_plus_decompressed_size_mod_800_plus_min_byte_value_times_2800(Path(BLOCK128K)), int)
