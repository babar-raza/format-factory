"""Sprint 260 ZST deepening tests."""
from pathlib import Path
import pytest, sys
_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))
zstandard = pytest.importorskip("zstandard")
from src.python.zst import (
    zst_file_size_mod_239_times_11_plus_decompressed_size_mod_3400_plus_max_byte_value_times_230,
    zst_compressed_size_times_18_plus_decompressed_size_mod_700_plus_min_byte_value_times_2600,
)
SAMPLES = _REPO / "samples/by-format/zst/valid"
BLOCK128K = SAMPLES / "block-128k.zst"
DICT_COMP = SAMPLES / "dict-compressed.zst"
EMPTY_BLK = SAMPLES / "empty-block.zst"

class TestZstMod239F1:
    def test_block128k_returns_int(self): assert isinstance(zst_file_size_mod_239_times_11_plus_decompressed_size_mod_3400_plus_max_byte_value_times_230(BLOCK128K), int)
    def test_block128k_expected_value(self): assert zst_file_size_mod_239_times_11_plus_decompressed_size_mod_3400_plus_max_byte_value_times_230(BLOCK128K) == 3067
    def test_dict_expected_value(self): assert zst_file_size_mod_239_times_11_plus_decompressed_size_mod_3400_plus_max_byte_value_times_230(DICT_COMP) == 29634
    def test_empty_expected_value(self): assert zst_file_size_mod_239_times_11_plus_decompressed_size_mod_3400_plus_max_byte_value_times_230(EMPTY_BLK) == 121
    def test_returns_nonnegative(self): assert zst_file_size_mod_239_times_11_plus_decompressed_size_mod_3400_plus_max_byte_value_times_230(EMPTY_BLK) >= 0
    def test_accepts_path_object(self): assert isinstance(zst_file_size_mod_239_times_11_plus_decompressed_size_mod_3400_plus_max_byte_value_times_230(Path(BLOCK128K)), int)

class TestZstTimes18F2:
    def test_block128k_returns_int(self): assert isinstance(zst_compressed_size_times_18_plus_decompressed_size_mod_700_plus_min_byte_value_times_2600(BLOCK128K), int)
    def test_block128k_expected_value(self): assert zst_compressed_size_times_18_plus_decompressed_size_mod_700_plus_min_byte_value_times_2600(BLOCK128K) == 2359626
    def test_dict_expected_value(self): assert zst_compressed_size_times_18_plus_decompressed_size_mod_700_plus_min_byte_value_times_2600(DICT_COMP) == 27992
    def test_empty_expected_value(self): assert zst_compressed_size_times_18_plus_decompressed_size_mod_700_plus_min_byte_value_times_2600(EMPTY_BLK) == 198
    def test_returns_nonnegative(self): assert zst_compressed_size_times_18_plus_decompressed_size_mod_700_plus_min_byte_value_times_2600(EMPTY_BLK) >= 0
    def test_accepts_path_object(self): assert isinstance(zst_compressed_size_times_18_plus_decompressed_size_mod_700_plus_min_byte_value_times_2600(Path(BLOCK128K)), int)
