"""Sprint 347 ZST deepening — test_r652.

Tests for:
  - zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950
  - zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250

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

_DICT  = _SAMPLES / "dict-compressed.zst"
_EMPTY = _SAMPLES / "empty-block.zst"
_BLOCK = _SAMPLES / "block-128k.zst"


def _skip_if_missing(p: Path) -> None:
    if not p.exists():
        pytest.skip(f"Sample not found: {p}")


# ---------------------------------------------------------------------------
# Function 1
# Formula: (file_size % 877) * 3300 + (decompressed_size % 9500) + max_byte_value * 950
# ---------------------------------------------------------------------------

class TestZstFileSizeMod877Times3300PlusDecompressedSizeMod9500PlusMaxByteValueTimes950:
    def test_dict_compressed(self):
        # (74%877)*3300 + (4160%9500) + 122*950 = 244200+4160+115900 = 364260
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950,
        )
        result = zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(_DICT)
        assert result == 364260

    def test_empty_block(self):
        # (11%877)*3300 + 0 + 0 = 36300
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950,
        )
        result = zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(_EMPTY)
        assert result == 36300

    def test_block_128k(self):
        # (131081%877)*3300 + (131068%9500) + 0 = 408*3300+7568 = 1353968
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950,
        )
        result = zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(_BLOCK)
        assert result == 1353968

    def test_returns_int(self):
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950,
        )
        assert isinstance(zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(_DICT), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950,
        )
        assert zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(_EMPTY) >= 0

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950,
        )
        assert zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(_DICT) > zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950,
        )
        assert isinstance(zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(str(_DICT)), int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950,
        )
        with pytest.raises(Exception):
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950("/nonexistent/path/file.zst")

    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950,
        )
        assert zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(_BLOCK) > zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950(_DICT)

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_file_size_mod_877_times_3300_plus_decompressed_size_mod_9500_plus_max_byte_value_times_950")


# ---------------------------------------------------------------------------
# Function 2
# Formula: (compressed_size % 881) * 2300 + (decompressed_size % 9900) + min_byte_value * 4250
# ---------------------------------------------------------------------------

class TestZstCompressedSizeMod881Times2300PlusDecompressedSizeMod9900PlusMinByteValueTimes4250:
    def test_dict_compressed(self):
        # (74%881)*2300 + (4160%9900) + 10*4250 = 170200+4160+42500 = 216860
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250,
        )
        result = zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(_DICT)
        assert result == 216860

    def test_empty_block(self):
        # (11%881)*2300 + 0 + 0 = 25300
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250,
        )
        result = zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(_EMPTY)
        assert result == 25300

    def test_block_128k(self):
        # (131081%881)*2300 + (131068%9900) + 0 = 693*2300+2368 = 1596268
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250,
        )
        result = zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(_BLOCK)
        assert result == 1596268

    def test_returns_int(self):
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250,
        )
        assert isinstance(zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(_DICT), int)

    def test_nonnegative(self):
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250,
        )
        assert zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(_EMPTY) >= 0

    def test_dict_greater_than_empty(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_EMPTY)
        from src.python.zst import (
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250,
        )
        assert zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(_DICT) > zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(_EMPTY)

    def test_path_string_accepted(self):
        _skip_if_missing(_DICT)
        from src.python.zst import (
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250,
        )
        assert isinstance(zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(str(_DICT)), int)

    def test_missing_file_raises(self):
        from src.python.zst import (
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250,
        )
        with pytest.raises(Exception):
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250("/nonexistent/path/file.zst")

    def test_block_greater_than_dict(self):
        _skip_if_missing(_DICT)
        _skip_if_missing(_BLOCK)
        from src.python.zst import (
            zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250,
        )
        assert zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(_BLOCK) > zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250(_DICT)

    def test_exported_in_init(self):
        import src.python.zst as zst_module
        assert hasattr(zst_module, "zst_compressed_size_mod_881_times_2300_plus_decompressed_size_mod_9900_plus_min_byte_value_times_4250")
