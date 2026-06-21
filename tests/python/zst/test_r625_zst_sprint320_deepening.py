"""Sprint 320 ZST deepening — test_r625.

Tests for:
  - zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210
  - zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13

Sample data:
  block-128k.zst:     csize=131081, dsize=131068, maxb=0, minb=0
  dict-compressed.zst: csize=74, dsize=4160, maxb=122, minb=10
  empty-block.zst:    csize=11, dsize=0, maxb=0, minb=0
"""
from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

_BLOCK = _SAMPLES / "block-128k.zst"
_DICT = _SAMPLES / "dict-compressed.zst"
_EMPTY = _SAMPLES / "empty-block.zst"


def _skip_if_missing(p: Path) -> None:
    if not p.exists():
        pytest.skip(f"Sample not found: {p}")


# ---------------------------------------------------------------------------
# Function 1: zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210
# Formula: (compressed_size % 467) * 29 + (decompressed_size % 7000) * 5 + max_byte_value * 210
# ---------------------------------------------------------------------------

class TestZstCompressedSizeMod467Times29PlusDecompressedMod7000Times5PlusMaxByteTimes210:
    def test_block_128k(self):
        # (131081 % 467) * 29 + (131068 % 7000) * 5 + 0 * 210 = 321*29 + 5068*5 = 9309 + 25340 = 34649
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210,
        )
        result = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(_BLOCK)
        assert result == 34649

    def test_dict_compressed(self):
        # (74 % 467) * 29 + (4160 % 7000) * 5 + 122 * 210 = 74*29 + 4160*5 + 25620 = 2146 + 20800 + 25620 = 48566
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210,
        )
        result = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(_DICT)
        assert result == 48566

    def test_empty_block(self):
        # (11 % 467) * 29 + (0 % 7000) * 5 + 0 * 210 = 319 + 0 + 0 = 319
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210,
        )
        result = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(_EMPTY)
        assert result == 319

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210,
        )
        result = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210,
        )
        result = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(_EMPTY)
        assert result >= 0

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210,
        )
        r_empty = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(_EMPTY)
        r_dict = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(_DICT)
        assert r_dict > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210,
        )
        result = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210,
        )
        with pytest.raises(Exception):
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(
                "/nonexistent/path/file.zst"
            )

    def test_block_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210,
        )
        r_empty = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(_EMPTY)
        r_block = zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210(_BLOCK)
        assert r_block > r_empty

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_mod_467_times_29_plus_decompressed_size_mod_7000_times_5_plus_max_byte_value_times_210")


# ---------------------------------------------------------------------------
# Function 2: zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13
# Formula: compressed_size * 33 + decompressed_size * 6 + max_byte_value * 13
# ---------------------------------------------------------------------------

class TestZstCompressedSizeTimes33PlusDecompressedTimes6PlusMaxByteTimes13:
    def test_block_128k(self):
        # 131081*33 + 131068*6 + 0*13 = 4325673 + 786408 = 5112081
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13,
        )
        result = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(_BLOCK)
        assert result == 5112081

    def test_dict_compressed(self):
        # 74*33 + 4160*6 + 122*13 = 2442 + 24960 + 1586 = 28988
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13,
        )
        result = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(_DICT)
        assert result == 28988

    def test_empty_block(self):
        # 11*33 + 0*6 + 0*13 = 363
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13,
        )
        result = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(_EMPTY)
        assert result == 363

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13,
        )
        result = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13,
        )
        result = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(_EMPTY)
        assert result >= 0

    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13,
        )
        r_dict = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(_DICT)
        r_block = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(_BLOCK)
        assert r_block > r_dict

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13,
        )
        result = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13,
        )
        with pytest.raises(Exception):
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(
                "/nonexistent/path/file.zst"
            )

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13,
        )
        r_empty = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(_EMPTY)
        r_dict = zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13(_DICT)
        assert r_dict > r_empty

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_times_33_plus_decompressed_size_times_6_plus_max_byte_value_times_13")
