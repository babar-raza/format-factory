"""Sprint 314 ZST deepening — test_r619.

Tests for:
  - zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100
  - zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7

Sample data:
  block-128k.zst: csize=131081, dsize=131068, maxb=0, minb=0
  dict-compressed.zst: csize=74, dsize=4160, maxb=122, minb=10
  empty-block.zst: csize=11, dsize=0, maxb=0, minb=0
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
# Function 1: zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100
# Formula: (compressed_size % 293) * 19 + (decompressed_size % 1000) * 3 + max_byte_value * 100
# ---------------------------------------------------------------------------

class TestZstCompressedSizeMod293Times19PlusDecompressedMod1000Times3PlusMaxByteTimes100:
    def test_block_128k(self):
        # (131081 % 293) * 19 + (131068 % 1000) * 3 + 0 * 100 = 110*19 + 68*3 + 0 = 2090 + 204 = 2294
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
        )
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_BLOCK)
        assert result == 2294

    def test_dict_compressed(self):
        # (74 % 293) * 19 + (4160 % 1000) * 3 + 122 * 100 = 74*19 + 160*3 + 12200 = 1406 + 480 + 12200 = 14086
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
        )
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_DICT)
        assert result == 14086

    def test_empty_block(self):
        # (11 % 293) * 19 + (0 % 1000) * 3 + 0 * 100 = 11*19 + 0 + 0 = 209
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
        )
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_EMPTY)
        assert result == 209

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
        )
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
        )
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_EMPTY)
        assert result >= 0

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
        )
        r_empty = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_EMPTY)
        r_dict = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_DICT)
        assert r_dict > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
        )
        result = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
        )
        with pytest.raises(Exception):
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(
                "/nonexistent/path/file.zst"
            )

    def test_block_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100,
        )
        r_empty = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_EMPTY)
        r_block = zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100(_BLOCK)
        assert r_block > r_empty

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_mod_293_times_19_plus_decompressed_size_mod_1000_times_3_plus_max_byte_value_times_100")


# ---------------------------------------------------------------------------
# Function 2: zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7
# Formula: compressed_size * 29 + decompressed_size * 3 + max_byte_value * 7
# ---------------------------------------------------------------------------

class TestZstCompressedSizeTimes29PlusDecompressedTimes3PlusMaxByteTimes7:
    def test_block_128k(self):
        # 131081*29 + 131068*3 + 0*7 = 3801349 + 393204 + 0 = 4194553
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
        )
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_BLOCK)
        assert result == 4194553

    def test_dict_compressed(self):
        # 74*29 + 4160*3 + 122*7 = 2146 + 12480 + 854 = 15480
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
        )
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_DICT)
        assert result == 15480

    def test_empty_block(self):
        # 11*29 + 0*3 + 0*7 = 319
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
        )
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_EMPTY)
        assert result == 319

    def test_returns_int(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
        )
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_EMPTY)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
        )
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_EMPTY)
        assert result >= 0

    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
        )
        r_dict = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_DICT)
        r_block = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_BLOCK)
        assert r_block > r_dict

    def test_path_string_accepted(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
        )
        result = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(str(_EMPTY))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
        )
        with pytest.raises(Exception):
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(
                "/nonexistent/path/file.zst"
            )

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_EMPTY)
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7,
        )
        r_empty = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_EMPTY)
        r_dict = zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7(_DICT)
        assert r_dict > r_empty

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_times_29_plus_decompressed_size_times_3_plus_max_byte_value_times_7")
