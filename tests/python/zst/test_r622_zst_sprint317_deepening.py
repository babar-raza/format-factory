"""Sprint 317 ZST deepening — test_r622.

Tests for:
  - zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200
  - zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11

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
# Function 1: zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200
# Formula: (compressed_size % 431) * 27 + (decompressed_size % 1100) * 5 + max_byte_value * 200
# ---------------------------------------------------------------------------

class TestZstCompressedSizeMod431Times27PlusDecompressedMod1100Times5PlusMaxByteTimes200:
    def test_block_128k(self):
        # (131081 % 431) * 27 + (131068 % 1100) * 5 + 0 * 200 = 57*27 + 168*5 = 1539 + 840 = 2379
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200,
        )
        result = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(_BLOCK)
        assert result == 2379

    def test_dict_compressed(self):
        # (74 % 431) * 27 + (4160 % 1100) * 5 + 122 * 200 = 74*27 + 860*5 + 24400 = 1998 + 4300 + 24400 = 30698
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200,
        )
        result = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(_DICT)
        assert result == 30698

    def test_empty_block(self):
        # (11 % 431) * 27 + (0 % 1100) * 5 + 0 * 200 = 297 + 0 + 0 = 297
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200,
        )
        result = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(_EMPTY)
        assert result == 297

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200,
        )
        result = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200,
        )
        result = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(_EMPTY)
        assert result >= 0

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200,
        )
        r_empty = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(_EMPTY)
        r_dict = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(_DICT)
        assert r_dict > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200,
        )
        result = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200,
        )
        with pytest.raises(Exception):
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(
                "/nonexistent/path/file.zst"
            )

    def test_block_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200,
        )
        r_empty = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(_EMPTY)
        r_block = zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200(_BLOCK)
        assert r_block > r_empty

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_mod_431_times_27_plus_decompressed_size_mod_1100_times_5_plus_max_byte_value_times_200")


# ---------------------------------------------------------------------------
# Function 2: zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11
# Formula: compressed_size * 31 + decompressed_size * 5 + max_byte_value * 11
# ---------------------------------------------------------------------------

class TestZstCompressedSizeTimes31PlusDecompressedTimes5PlusMaxByteTimes11:
    def test_block_128k(self):
        # 131081*31 + 131068*5 + 0*11 = 4063511 + 655340 = 4718851
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11,
        )
        result = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(_BLOCK)
        assert result == 4718851

    def test_dict_compressed(self):
        # 74*31 + 4160*5 + 122*11 = 2294 + 20800 + 1342 = 24436
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11,
        )
        result = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(_DICT)
        assert result == 24436

    def test_empty_block(self):
        # 11*31 + 0*5 + 0*11 = 341
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11,
        )
        result = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(_EMPTY)
        assert result == 341

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11,
        )
        result = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11,
        )
        result = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(_EMPTY)
        assert result >= 0

    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11,
        )
        r_dict = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(_DICT)
        r_block = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(_BLOCK)
        assert r_block > r_dict

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11,
        )
        result = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11,
        )
        with pytest.raises(Exception):
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(
                "/nonexistent/path/file.zst"
            )

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11,
        )
        r_empty = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(_EMPTY)
        r_dict = zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11(_DICT)
        assert r_dict > r_empty

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_times_31_plus_decompressed_size_times_5_plus_max_byte_value_times_11")
