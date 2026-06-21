"""
tests/python/deepening/test_r800_zst_sprint248_deepening.py

Sprint: sal-advancement-iter13-20260617-171000-8656416
Product deepening Sprint 248 — 2 new ZST analytics functions.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
pytest.importorskip("zstandard", reason="python-zstandard not installed")

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from zst import (
    zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180,
    zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500,
)

_ZST_DIR = _REPO / "samples" / "by-format" / "zst" / "valid"
_BLOCK = str(_ZST_DIR / "block-128k.zst")
_DICT = str(_ZST_DIR / "dict-compressed.zst")
_EMPTY = str(_ZST_DIR / "empty-block.zst")


class TestZstMod179F1:
    """zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180"""

    def test_block_returns_int(self):
        result = zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180(_BLOCK)
        assert isinstance(result, int)

    def test_block_expected_value(self):
        # fs=131081, ds=131068, cs=131081, mb=0
        # (131081%179)*5 + (131068%2700) + 0*180 = (131081%179=131081-732*179=131081-131028=53)*5=265
        # 131068%2700=131068-48*2700=131068-129600=1468
        # result=265+1468+0=1733
        result = zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180(_BLOCK)
        assert result == 1733

    def test_dict_expected_value(self):
        # fs=74, ds=4160, mb=122
        # (74%179)*5 + (4160%2700) + 122*180 = 74*5=370 + 1460 + 21960 = 23790
        result = zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180(_DICT)
        assert result == 23790

    def test_empty_expected_value(self):
        # fs=11, ds=0, mb=0 → (11%179)*5 + (0%2700) + 0 = 55+0+0=55
        result = zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180(_EMPTY)
        assert result == 55

    def test_returns_nonnegative(self):
        for path in [_BLOCK, _DICT, _EMPTY]:
            result = zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180(path)
            assert result >= 0

    def test_accepts_path_object(self):
        result = zst_file_size_mod_179_times_5_plus_decompressed_size_mod_2700_plus_max_byte_value_times_180(Path(_EMPTY))
        assert result == 55


class TestZstMod181F2:
    """zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500"""

    def test_block_returns_int(self):
        result = zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(_BLOCK)
        assert isinstance(result, int)

    def test_block_expected_value(self):
        # cs=131081, ds=131068, mn=0
        # (131081%181)*10 + (131068%2800) + 0*1500
        # 131081%181 = 131081-724*181=131081-131044=37; 37*10=370
        # 131068%2800=131068-46*2800=131068-128800=2268
        # result=370+2268+0=2638
        result = zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(_BLOCK)
        assert result == 2638

    def test_dict_expected_value(self):
        # cs=74, ds=4160, mn=10
        # (74%181)*10 + (4160%2800) + 10*1500 = 74*10=740 + 1360 + 15000 = 17100
        result = zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(_DICT)
        assert result == 17100

    def test_empty_expected_value(self):
        # cs=11, ds=0, mn=0 → (11%181)*10 + (0%2800) + 0 = 110+0+0=110
        result = zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(_EMPTY)
        assert result == 110

    def test_returns_nonnegative(self):
        for path in [_BLOCK, _DICT, _EMPTY]:
            result = zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(path)
            assert result >= 0

    def test_accepts_path_object(self):
        result = zst_compressed_size_mod_181_times_10_plus_decompressed_size_mod_2800_plus_min_byte_value_times_1500(Path(_EMPTY))
        assert result == 110
