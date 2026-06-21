"""Sprint 341 ZST deepening — test_r646.

Tests for:
  - zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850
  - zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750

Sample data (samples/by-format/zst/valid/):
  dict-compressed.zst: fs=74, cs=74, ds=4160, max_byte=122, min_byte=10
  empty-block.zst:     fs=11, cs=11, ds=0,    max_byte=0,   min_byte=0
  block-128k.zst:      fs=131081, cs=131081, ds=131068, max_byte=0, min_byte=0
"""
from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_SAMPLES = _REPO / "samples" / "by-format" / "zst" / "valid"

_DICT = _SAMPLES / "dict-compressed.zst"
_EMPTY = _SAMPLES / "empty-block.zst"
_BLOCK = _SAMPLES / "block-128k.zst"


def _skip_if_missing(p: Path) -> None:
    if not p.exists():
        pytest.skip(f"Sample not found: {p}")


# ---------------------------------------------------------------------------
# Function 1: zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850
# Formula: (file_size % 839) * 3100 + (decompressed_size % 9300) + max_byte_value * 850
# ---------------------------------------------------------------------------

class TestZstFileSizeMod839Times3100PlusDecompressedSizeMod9300PlusMaxByteValueTimes850:
    def test_dict_compressed(self):
        # (74 % 839)*3100 + (4160 % 9300) + 122*850 = 229400 + 4160 + 103700 = 337260
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850,
        )
        result = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(_DICT)
        assert result == 337260

    def test_empty_block(self):
        # (11 % 839)*3100 + (0 % 9300) + 0*850 = 34100
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850,
        )
        result = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(_EMPTY)
        assert result == 34100

    def test_block_128k(self):
        # (131081 % 839)*3100 + (131068 % 9300) + 0*850 = 197*3100 + 868 = 610700 + 868 = 611568
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850,
        )
        result = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(_BLOCK)
        assert result == 611568

    def test_returns_int(self):
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850,
        )
        result = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(_DICT)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850,
        )
        result = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(_EMPTY)
        assert result >= 0

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850,
        )
        r_dict = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(_DICT)
        r_empty = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(_EMPTY)
        assert r_dict > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850,
        )
        result = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(str(_DICT))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850,
        )
        with pytest.raises(Exception):
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(
                "/nonexistent/path/file.zst"
            )

    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850,
        )
        r_dict = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(_DICT)
        r_block = zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850(_BLOCK)
        assert r_block > r_dict

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_file_size_mod_839_times_3100_plus_decompressed_size_mod_9300_plus_max_byte_value_times_850")


# ---------------------------------------------------------------------------
# Function 2: zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750
# Formula: (compressed_size % 857) * 2100 + (decompressed_size % 9800) + min_byte_value * 3750
# ---------------------------------------------------------------------------

class TestZstCompressedSizeMod857Times2100PlusDecompressedSizeMod9800PlusMinByteValueTimes3750:
    def test_dict_compressed(self):
        # (74 % 857)*2100 + (4160 % 9800) + 10*3750 = 155400 + 4160 + 37500 = 197060
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750,
        )
        result = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(_DICT)
        assert result == 197060

    def test_empty_block(self):
        # (11 % 857)*2100 + (0 % 9800) + 0*3750 = 23100
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750,
        )
        result = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(_EMPTY)
        assert result == 23100

    def test_block_128k(self):
        # (131081 % 857)*2100 + (131068 % 9800) + 0*3750 = 817*2100 + 3668 = 1715700 + 3668 = 1719368
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750,
        )
        result = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(_BLOCK)
        assert result == 1719368

    def test_returns_int(self):
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750,
        )
        result = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(_DICT)
        assert isinstance(result, int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750,
        )
        result = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(_EMPTY)
        assert result >= 0

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750,
        )
        r_dict = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(_DICT)
        r_empty = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(_EMPTY)
        assert r_dict > r_empty

    def test_path_string_accepted(self):
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750,
        )
        result = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(str(_DICT))
        assert isinstance(result, int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750,
        )
        with pytest.raises(Exception):
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(
                "/nonexistent/path/file.zst"
            )

    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750,
        )
        r_dict = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(_DICT)
        r_block = zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750(_BLOCK)
        assert r_block > r_dict

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_mod_857_times_2100_plus_decompressed_size_mod_9800_plus_min_byte_value_times_3750")
