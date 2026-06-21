"""Sprint 329 ZST deepening — test_r634.

Tests for:
  - zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225
  - zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17

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
# Function 1: zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225
# Formula: (compressed_size % 523) * 31 + (decompressed_size % 7800) * 5 + max_byte_value * 215
# ---------------------------------------------------------------------------

class TestZstCompressedSizeMod523Times31PlusDecompressedMod7800Times5PlusMaxByteTimes215:
    def test_block_128k(self):
        # (131081 % 523) * 31 + (131068 % 7800) * 5 + 0 * 215 = 41601
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225,
        )
        result = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(_BLOCK)
        assert result == 46106

    def test_dict_compressed(self):
        # (74 % 523) * 31 + (4160 % 7800) * 5 + 122 * 215 = 49324
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225,
        )
        result = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(_DICT)
        assert result == 50544

    def test_empty_block(self):
        # (11 % 523) * 31 + (0 % 7800) * 5 + 0 * 215 = 341
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225,
        )
        result = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(_EMPTY)
        assert result == 341

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225,
        )
        result = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225,
        )
        result = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(_EMPTY)
        assert result >= 0

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225,
        )
        r_empty = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(_EMPTY)
        r_dict = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(_DICT)
        assert r_dict > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225,
        )
        result = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225,
        )
        with pytest.raises(Exception):
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(
                "/nonexistent/path/file.zst"
            )

    def test_block_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225,
        )
        r_empty = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(_EMPTY)
        r_block = zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225(_BLOCK)
        assert r_block > r_empty

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_mod_557_times_31_plus_decompressed_size_mod_8200_times_5_plus_max_byte_value_times_225")


# ---------------------------------------------------------------------------
# Function 2: zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17
# Formula: compressed_size * 35 + decompressed_size * 7 + max_byte_value * 15
# ---------------------------------------------------------------------------

class TestZstCompressedSizeTimes35PlusDecompressedTimes7PlusMaxByteTimes15:
    def test_block_128k(self):
        # 131081*35 + 131068*7 + 0*15 = 4587835 + 917476 = 5505311
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17,
        )
        result = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(_BLOCK)
        assert result == 6291771

    def test_dict_compressed(self):
        # 74*35 + 4160*7 + 122*15 = 2590 + 29120 + 1830 = 33540
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17,
        )
        result = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(_DICT)
        assert result == 42400

    def test_empty_block(self):
        # 11*35 + 0*7 + 0*15 = 385
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17,
        )
        result = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(_EMPTY)
        assert result == 429

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17,
        )
        result = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17,
        )
        result = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(_EMPTY)
        assert result >= 0

    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17,
        )
        r_dict = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(_DICT)
        r_block = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(_BLOCK)
        assert r_block > r_dict

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17,
        )
        result = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17,
        )
        with pytest.raises(Exception):
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(
                "/nonexistent/path/file.zst"
            )

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17,
        )
        r_empty = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(_EMPTY)
        r_dict = zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17(_DICT)
        assert r_dict > r_empty

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_times_39_plus_decompressed_size_times_9_plus_max_byte_value_times_17")
